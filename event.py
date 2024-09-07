# event.py
import time
from function import get_db_connection


def setup_events(bot):
    @bot.event
    async def on_voice_state_update(member, before, after):
        """監聽成員的語音事件，並在資料庫上 + 1"""
        if after.channel is not None:
            conn, c = get_db_connection()
            c.execute('UPDATE user_activity SET voiceCount = voiceCount + 1, lastTime = ? WHERE userID = ?',
                      (int(time.time()), member.id))
            conn.commit()
            conn.close()

        if before:  # 單純看警報不爽，此行代碼沒有意義
            pass

    @bot.event
    async def on_message(message):
        """監聽成員發言事件，並在資料庫上 + 1"""
        if message.author == bot.user:
            return

        conn, c = get_db_connection()
        c.execute('UPDATE user_activity SET textCount = textCount + 1, lastTime = ? WHERE userID = ?',
                  (int(time.time()), message.author.id))
        conn.commit()
        conn.close()

    @bot.event
    async def on_member_join(member):
        """當新成員加入時，將其新增至資料庫"""
        conn, c = get_db_connection()
        c.execute('INSERT OR IGNORE INTO user_activity (userID, userName) VALUES (?, ?)',
                  (member.id, str(member)))  # 使用 INSERT OR IGNORE 以避免重複新增
        conn.commit()
        conn.close()
        print(f"{member.name} 已加入伺服器並已添加到資料庫。")
