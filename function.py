# function.py
import os
import time
import asyncio
import sqlite3
import discord
from datetime import datetime
from config import RESET_TIME, CHECK_RESET_TIME


# 資料庫連接函式
def get_db_connection():
    """返回 資料庫連接 和 資料指標"""
    conn = sqlite3.connect('user_activity.db', timeout=10)
    c = conn.cursor()
    return conn, c


def check_db(bot, guild_id, db_path='user_activity.db'):
    """檢查數資料庫文件是否存在，如果不存在則初始化數據庫"""
    if not os.path.exists(db_path):
        print("資料庫文件不存在，正在初始化...")
        init_db(bot, guild_id)
    else:
        print("資料庫已存在。")


# 初始化資料庫
def init_db(bot, guild_id):
    """初始化資料庫，並將所有成員新增到資料庫"""
    conn, c = get_db_connection()

    # 建立 用戶活動紀錄表
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_activity (
            userID INTEGER PRIMARY KEY,
            userName TEXT,
            voiceCount INTEGER DEFAULT 0,
            textCount INTEGER DEFAULT 0,
            lastTime INTEGER
        )
    ''')

    # 建立 重置時間表
    c.execute('''
        CREATE TABLE IF NOT EXISTS reset_schedule (
            next_reset INTEGER
        )
    ''')

    # 設定 下次重設時間（'RESET_TIME' 天後）
    next_reset = int(time.time()) + RESET_TIME * 24 * 60 * 60
    c.execute('INSERT INTO reset_schedule (next_reset) VALUES (?)', (next_reset,))
    conn.commit()
    conn.close()

    # 將所有成員新增到資料庫
    add_all_members_to_db(bot, guild_id)


# 將所有成員新增到資料庫的函式
def add_all_members_to_db(bot, guild_id):
    """將所有公會成員新增到資料庫"""
    conn, c = get_db_connection()

    guild = bot.get_guild(guild_id)

    # 檢查 是否成功取得到伺服器資料
    if guild is not None:
        for member in guild.members:
            # 插入 成員訊息，避免重複（IGNORE 防止已有記錄重複插入）
            c.execute('INSERT OR IGNORE INTO user_activity (userID, userName) VALUES (?, ?)',
                      (member.id, str(member)))

        conn.commit()
    else:
        print(f"無法獲取伺服器 ID 為 {guild_id} 的資料")

    conn.close()


# 生成 成員活動報告的函式
async def generate_user_activity_report(interaction: discord.Interaction):
    """產生成員活動報告並發送到 Discord"""
    conn, c = get_db_connection()

    # 取得 下次重設時間
    c.execute('SELECT next_reset FROM reset_schedule')
    result = c.fetchone()

    if result:
        next_reset_timestamp = result[0]
        remaining_time = next_reset_timestamp - int(time.time())
    else:
        remaining_time = 0

    # 取得 所有成員資料
    c.execute('SELECT * FROM user_activity')
    users_data = c.fetchall()

    active_users = []
    inactive_users = []

    # 根據成員活動狀態 將成員分類
    for user in users_data:
        if user[2] > 0 or user[3] > 0:
            active_users.append(user)
        else:
            inactive_users.append(user)

    # 產生報告
    report_filename = "user_activity_report.txt"

    with open(report_filename, 'w', encoding='utf-8') as report_file:
        report_file.write("用戶活動數據報告:\n\n")
        report_file.write(f"剩餘重置時間: {remaining_time // 3600} 小時\n")

        # 新增 活躍成員
        report_file.write("\n活躍成員:\n")
        report_file.write(f"{'用戶名':<38} | {'語音次數':<12} | {'文字次數':<12} | {'最後活動時間'}\n")
        report_file.write("-" * 100 + "\n")

        for user in active_users:
            last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user[4])) if user[4] else "無"
            report_file.write(f"{user[1]:<40} | {user[2]:<15} | {user[3]:<14} | {last_time}\n")

        # 新增 不活躍成員
        report_file.write("\n不活躍成員:\n")
        report_file.write(f"{'用戶名':<38} | {'語音次數':<12} | {'文字次數':<12} | {'最後活動時間'}\n")
        report_file.write("-" * 100 + "\n")

        for user in inactive_users:
            last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user[4])) if user[4] else "無"
            report_file.write(f"{user[1]:<40} | {user[2]:<15} | {user[3]:<14} | {last_time}\n")

    conn.close()

    # 發送 輸出文件到 Discord
    await interaction.response.send_message("即時用戶活動數已產生，請查看附件。", file=discord.File(report_filename), ephemeral=True)


# 重設 用戶活動的函數
async def reset_user_activity(bot, guild_id):
    """重置成員活動數據，並將所有成員重新添加到資料庫"""
    conn, c = get_db_connection()

    # 取得 所有成員資料
    c.execute('SELECT * FROM user_activity')
    users_data = c.fetchall()

    # 確保 ./csv 目錄存在
    os.makedirs('./csv', exist_ok=True)

    # 產生 時間戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"./csv/user_activity_report_{timestamp}.csv"

    # 輸出 成員活動數據到 CSV
    with open(csv_filename, 'w', encoding='utf-8') as csv_file:
        csv_file.write(f"{'USER_ID'}{'USER_NAME'},{'JOIN_VOICE_CHANNEL'},{'SENT_TEXT_TO_CHANNEL'},{'LAST_TIME'}\n")
        for user in users_data:
            last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user[4])) if user[4] else "NONE"
            line = f"{user[0]},{user[1]},{user[2]},{user[3]},{last_time}\n"
            csv_file.write(line)

    # 重設 成員活動數據
    c.execute('UPDATE user_activity SET voiceCount = 0, textCount = 0, lastTime = NULL')
    conn.commit()
    conn.close()

    # 將所有成員重新新增到資料庫
    add_all_members_to_db(bot, guild_id)

    return csv_filename


# 檢查 下次重設時間的函式
async def check_next_reset(interaction: discord.Interaction):
    """檢查並返回下次重設時間"""
    conn, c = get_db_connection()

    # 獲取 下次重設時間
    c.execute('SELECT next_reset FROM reset_schedule')
    result = c.fetchone()

    if result:
        next_reset_timestamp = result[0]
        next_reset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_reset_timestamp))
        await interaction.response.send_message(f"下次重設時間為：{next_reset_time}（UTC）", ephemeral=True)
    else:
        await interaction.response.send_message("無法取得下次重設時間。", ephemeral=True)

    conn.close()


# 檢查下次重設時間的任務
async def check_reset_schedule(bot, guild_id):
    """每分鐘檢查一次重置時間，判斷是否需要重設"""
    while True:
        await asyncio.sleep(CHECK_RESET_TIME * 60)  # 每 'CHECK_RESET_TIME' 分鐘檢查一次
        conn, c = get_db_connection()

        # 檢查是否到達下次重設時間
        c.execute('SELECT next_reset FROM reset_schedule')
        result = c.fetchone()

        if result:
            next_reset_timestamp = result[0]
            if int(time.time()) >= next_reset_timestamp:
                # 重設成員活動資料
                await reset_user_activity(bot, guild_id)
                print("成員活動報告已重設，CSV 文件已產生")

                # 設定下次重設時間（ 'RESET_TIME' 天後）
                next_reset = int(time.time()) + RESET_TIME * 24 * 60 * 60
                c.execute('UPDATE reset_schedule SET next_reset = ?', (next_reset,))
                conn.commit()

        conn.close()
