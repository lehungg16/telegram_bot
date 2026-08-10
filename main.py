"""
main.py
Khởi tạo bot, kết nối Telegram Bot API, đăng ký các handler.

Giai đoạn 1: chạy bằng polling để test local (theo checklist).
Giai đoạn 5: sẽ đổi sang webhook khi deploy lên Render.
"""
import logging

from telegram.ext import Application, CommandHandler

from config import TELEGRAM_TOKEN
from handlers.start import start_command
from handlers.help import help_command

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_app() -> Application:
    """Tạo Application và đăng ký toàn bộ handler.

    Tách hàm riêng để sau này Giai đoạn 5 (webhook) có thể tái sử dụng
    cùng một Application mà không phải viết lại phần đăng ký handler.
    """
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Mỗi lệnh có handler riêng trong thư mục handlers/ — dễ thêm lệnh mới
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    return app


def main() -> None:
    app = build_app()
    logger.info("Bot đang chạy (polling)... Nhấn Ctrl+C để dừng.")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
