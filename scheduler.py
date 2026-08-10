"""
scheduler.py
Quản lý việc lên lịch / huỷ lịch nhắc nhở bằng JobQueue (chạy nền trên APScheduler,
đã tích hợp sẵn trong python-telegram-bot).

Mỗi job được đặt tên theo quy ước "reminder_<chat_id>" để dễ tìm và xoá.
"""
import logging

from telegram.ext import ContextTypes, JobQueue

from reminder_messages import get_random_message
from utils.time_utils import parse_hhmm

logger = logging.getLogger(__name__)


def _job_name(chat_id: int) -> str:
    return f"reminder_{chat_id}"


async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hàm callback JobQueue gọi mỗi khi đến giờ nhắc."""
    chat_id = context.job.chat_id
    try:
        await context.bot.send_message(chat_id=chat_id, text=get_random_message())
    except Exception:
        logger.exception("Gửi nhắc nhở thất bại cho chat_id=%s", chat_id)


def schedule_reminder(job_queue: JobQueue, chat_id: int, time_str: str) -> bool:
    """Tạo (hoặc thay thế) lịch nhắc hằng ngày cho 1 chat_id.

    Trả về True nếu lên lịch thành công, False nếu time_str sai định dạng.
    """
    parsed_time = parse_hhmm(time_str)
    if parsed_time is None:
        return False

    # Xoá job cũ (nếu có) trước khi tạo job mới, tránh trùng lịch
    remove_reminder(job_queue, chat_id)

    job_queue.run_daily(
        send_reminder,
        time=parsed_time,
        chat_id=chat_id,
        name=_job_name(chat_id),
    )
    return True


def remove_reminder(job_queue: JobQueue, chat_id: int) -> None:
    for job in job_queue.get_jobs_by_name(_job_name(chat_id)):
        job.schedule_removal()


def restore_all_reminders(job_queue: JobQueue) -> int:
    """Đọc file cấu hình và dựng lại lịch cho những người đã bật nhắc nhở.
    Gọi 1 lần khi bot khởi động (kể cả sau khi Render restart)."""
    import storage

    data = storage.load_all()
    count = 0
    for chat_id_str, cfg in data.items():
        if cfg.get("enabled"):
            ok = schedule_reminder(job_queue, int(chat_id_str), cfg.get("time", storage.DEFAULT_TIME))
            if ok:
                count += 1
    return count
