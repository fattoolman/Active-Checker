# command.py
import discord
from function import generate_user_activity_report, reset_user_activity, check_next_reset
from config import GUILD_ID


def setup_commands(bot):
    @bot.tree.command(name="time", description="查詢下次重設時間")
    async def check_next_reset_command(interaction: discord.Interaction):
        await check_next_reset(interaction)

    @bot.tree.command(name="report", description="產生即時成員活動報告")
    async def report_command(interaction: discord.Interaction):
        await generate_user_activity_report(interaction)

    @bot.tree.command(name="reset", description="重設成員活動數據並輸出 CSV")
    async def reset_command(interaction: discord.Interaction):
        # 檢查成員是否為管理員
        if any(role.permissions.administrator for role in interaction.user.roles):
            try:
                csv_filename = await reset_user_activity(bot, GUILD_ID)  # 調用 重設函數，傳入 bot 和 GUILD_ID
                await interaction.followup.send(
                    f"用戶活動數據已重設，CSV 文件已產生：",
                    file=discord.File(csv_filename),
                    ephemeral=True
                )
            except Exception as e:
                await interaction.followup.send(f"發生錯誤：{str(e)}", ephemeral=True)
