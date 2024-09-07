# main.py
import discord
from discord.ext import commands
import asyncio

from function import check_db, check_reset_schedule
from command import setup_commands
from event import setup_events
from config import *


# 設定機器人
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# 建立 bot Instance
bot = commands.Bot(command_prefix="!", intents=intents)


# 初始化資料庫和命令
@bot.event
async def on_ready():
    """當 bot 已經準備好"""
    print(f'登入為 {bot.user}')

    # 檢查數據庫資料，傳入 bot 和 GUILD_ID
    check_db(bot, GUILD_ID)

    # 同步應用指令
    await bot.tree.sync()
    print("指令已成功註冊！")

    # 啟動檢查重設時間的背景任務
    await asyncio.create_task(check_reset_schedule(bot, GUILD_ID))


# 設定 命令 和 事件
setup_commands(bot)
setup_events(bot)

# 啟動機器人
bot.run(TOKEN)
