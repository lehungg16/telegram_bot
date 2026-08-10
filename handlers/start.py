"""
handlers/start.py
Lệnh /start — chào mừng, hướng dẫn sơ lược cách dùng.
"""
from telegram import Update
from telegram.ext import ContextTypes

WELCOME_MESSAGE = (
    "👋 Xin chào! Mình là thư ký My.\n\n"
    "Hiện tại mình có thể:\n"
    "• Nhắc nhở sức khỏe theo giờ bạn đặt (sắp ra mắt)\n"
    "• Lấy tin mới từ group Facebook (sắp ra mắt)\n\n"
    "Gõ /help để xem toàn bộ danh sách lệnh."
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_MESSAGE)
