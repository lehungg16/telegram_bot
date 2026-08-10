"""
handlers/help.py
Lệnh /help — liệt kê toàn bộ lệnh kèm mô tả ngắn.
Đọc từ handlers/commands.py để luôn đồng bộ với danh sách lệnh thật.
"""
from telegram import Update
from telegram.ext import ContextTypes

from handlers.commands import COMMANDS


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lines = ["📋 Danh sách lệnh:\n"]
    for cmd, desc in COMMANDS:
        lines.append(f"/{cmd} — {desc}")
    await update.message.reply_text("\n".join(lines))
