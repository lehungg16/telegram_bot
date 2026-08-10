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
from handlers.reminder import nhacnho_bat_command, nhacnho_tat_command, setgio_command
from scheduler import restore_all_reminders
from handlers.baiviet import baiviet_command
from telegram.ext import CallbackQueryHandler
from handlers.menu import menu_command, menu_callback_handler
from handlers.menu_callback import menu_callback
from telegram.ext import CallbackQueryHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def _on_startup(app: Application) -> None:
    """Chạy 1 lần khi bot khởi động — dựng lại lịch nhắc cho những người
    đã bật trước đó, kể cả sau khi Render restart/deploy lại."""
    count = restore_all_reminders(app.job_queue)
    logger.info("Đã khôi phục %d lịch nhắc nhở.", count)


def build_app() -> Application:
    """Tạo Application và đăng ký toàn bộ handler.

    Tách hàm riêng để sau này Giai đoạn 5 (webhook) có thể tái sử dụng
    cùng một Application mà không phải viết lại phần đăng ký handler.
    """
    app = Application.builder().token(TELEGRAM_TOKEN).post_init(_on_startup).build()

    # Mỗi lệnh có handler riêng trong thư mục handlers/ — dễ thêm lệnh mới
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CallbackQueryHandler(menu_callback_handler))
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("baiviet", baiviet_command))
    app.add_handler(CommandHandler("nhacnho_bat", nhacnho_bat_command))
    app.add_handler(CommandHandler("nhacnho_tat", nhacnho_tat_command))
    app.add_handler(CommandHandler("setgio", setgio_command))

    return app


def main() -> None:
    app = build_app()
    logger.info("Bot đang chạy (polling)... Nhấn Ctrl+C để dừng.")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
