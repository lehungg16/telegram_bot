"""
handlers/reminder.py
3 lệnh nhắc nhở sức khỏe: /nhacnho_bat, /nhacnho_tat, /setgio HH:MM
"""
import storage
from scheduler import schedule_reminder, remove_reminder
from telegram import Update
from telegram.ext import ContextTypes


async def nhacnho_bat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    cfg = storage.get_user(chat_id)
    time_str = cfg["time"]

    ok = schedule_reminder(context.job_queue, chat_id, time_str)
    if not ok:
        # Không nên xảy ra vì time_str luôn được validate lúc lưu, nhưng phòng hờ
        await update.message.reply_text("⚠️ Giờ nhắc đang lưu bị lỗi, hãy đặt lại bằng /setgio HH:MM")
        return

    storage.set_user(chat_id, enabled=True)
    await update.message.reply_text(
        f"✅ Đã bật nhắc nhở sức khỏe, mỗi ngày lúc {time_str}.\n"
        f"Dùng /setgio HH:MM để đổi giờ, /nhacnho_tat để tắt."
    )


async def nhacnho_tat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    remove_reminder(context.job_queue, chat_id)
    storage.set_user(chat_id, enabled=False)
    await update.message.reply_text("🔕 Đã tắt nhắc nhở sức khỏe. Dùng /nhacnho_bat để bật lại.")


async def setgio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    if not context.args:
        await update.message.reply_text("Cú pháp: /setgio HH:MM\nVí dụ: /setgio 21:00")
        return

    time_str = context.args[0]
    cfg = storage.get_user(chat_id)

    if cfg["enabled"]:
        # Đang bật sẵn -> áp dụng giờ mới ngay lập tức
        ok = schedule_reminder(context.job_queue, chat_id, time_str)
        if not ok:
            await update.message.reply_text("⚠️ Sai định dạng giờ. Dùng dạng HH:MM, ví dụ: /setgio 07:30")
            return
        storage.set_user(chat_id, time=time_str)
        await update.message.reply_text(f"⏰ Đã đổi giờ nhắc sang {time_str} (đang bật).")
    else:
        # Chưa bật -> chỉ validate và lưu giờ, chưa tạo job
        from utils.time_utils import parse_hhmm
        if parse_hhmm(time_str) is None:
            await update.message.reply_text("⚠️ Sai định dạng giờ. Dùng dạng HH:MM, ví dụ: /setgio 07:30")
            return
        storage.set_user(chat_id, time=time_str)
        await update.message.reply_text(
            f"⏰ Đã lưu giờ nhắc {time_str}. Dùng /nhacnho_bat để bật nhắc nhở."
        )
