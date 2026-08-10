# handlers/menu_callback.py
"""
File này xử lý mọi lượt bấm nút trong menu inline (/menu).
Chỉ cần import và add_handler(CallbackQueryHandler(menu_callback))
trong main.py là chạy được.

Ưu tiên: nút MCP đã xong 100%, không cần sửa gì thêm.
Các nút còn lại mình nối tạm vào tên hàm suy đoán theo cấu trúc
project của bạn trong StruckFile.txt — bạn xem phần TODO bên dưới
để xác nhận / sửa lại tên hàm cho khớp code thật.
"""

from telegram import Update
from telegram.ext import ContextTypes

# TODO: kiểm tra lại đường dẫn import này có đúng với cấu trúc
# handlers/reminder.py và handlers/baiviet.py của bạn không.
# Nếu tên hàm khác, chỉ cần sửa 2 dòng import + 2 dòng gọi hàm bên dưới.
try:
    from handlers.reminder import bat_nhac_nho, tat_nhac_nho, hoi_gio_nhac
except ImportError:
    bat_nhac_nho = tat_nhac_nho = hoi_gio_nhac = None

try:
    from handlers.baiviet import xem_bai_viet
except ImportError:
    xem_bai_viet = None


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data  # callback_data của nút vừa bấm

    # ----- MCP: chưa làm, trả thông báo cố định -----
    if data == "mcp":
        await query.answer()  # tắt icon loading trên nút
        await query.edit_message_text("My chưa làm được !!! 🙈")
        return

    # ----- Xem bài viết -----
    if data == "baiviet":
        await query.answer()
        if xem_bai_viet:
            await xem_bai_viet(update, context)
        else:
            # TODO: gửi tên hàm thật trong handlers/baiviet.py nếu khác
            await query.edit_message_text("My chưa làm được !!! 🙈")
        return

    # ----- Bật nhắc nhở -----
    if data == "nhacnho_bat":
        await query.answer()
        if bat_nhac_nho:
            await bat_nhac_nho(update, context)
        else:
            # TODO: gửi tên hàm thật trong handlers/reminder.py nếu khác
            await query.edit_message_text("My chưa làm được !!! 🙈")
        return

    # ----- Tắt nhắc nhở -----
    if data == "nhacnho_tat":
        await query.answer()
        if tat_nhac_nho:
            await tat_nhac_nho(update, context)
        else:
            await query.edit_message_text("My chưa làm được !!! 🙈")
        return

    # ----- Đặt giờ nhắc -----
    if data == "setgio":
        await query.answer()
        if hoi_gio_nhac:
            await hoi_gio_nhac(update, context)
        else:
            await query.edit_message_text("My chưa làm được !!! 🙈")
        return

    # ----- Nút lạ / chưa định nghĩa -----
    await query.answer()
    await query.edit_message_text("My chưa làm được !!! 🙈")
