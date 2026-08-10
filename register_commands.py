"""
register_commands.py
Đăng ký danh sách lệnh với BotFather để hiện menu "/" khi người dùng gõ.

Chạy 1 lần (hoặc mỗi khi thêm lệnh mới):
    python register_commands.py
"""
import asyncio

from telegram import BotCommand
from telegram.ext import Application

from config import TELEGRAM_TOKEN
from handlers.commands import COMMANDS


async def register() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    bot_commands = [BotCommand(cmd, desc) for cmd, desc in COMMANDS]
    await app.bot.set_my_commands(bot_commands)
    print(f"Đã đăng ký {len(bot_commands)} lệnh với BotFather:")
    for cmd, desc in COMMANDS:
        print(f"  /{cmd} — {desc}")


if __name__ == "__main__":
    asyncio.run(register())
