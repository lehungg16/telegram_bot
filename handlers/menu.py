"""
handlers/menu.py
------------------
Xử lý lệnh /menu — hiện ra 1 bảng nút bấm (Inline Keyboard) để
người dùng chọn nhanh chức năng, thay vì phải nhớ gõ từng lệnh /.

CÁCH PHẢN HỒI: khi bấm nút, tin nhắn GỐC (chứa các nút bấm) sẽ
tự ĐỔI NỘI DUNG tại chỗ (dùng query.edit_message_text), giống
cách BotFather làm khi bấm "Edit Commands" - không gửi thêm 1
tin nhắn mới bên dưới.

CHỐNG TREO "ĐANG TẢI...": query.answer() được gọi NGAY DÒNG ĐẦU
TIÊN trong try, và toàn bộ phần xử lý còn lại được bọc trong
try/except riêng - đảm bảo dù có lỗi bất kỳ ở đâu, Telegram vẫn
luôn nhận được phản hồi, nút bấm không bao giờ bị kẹt ở trạng
thái loading vô thời hạn.

VỀ VIỆC GỌI LẠI /nhacnho_bat VÀ /nhacnho_tat:
Chưa có nội dung thật của handlers/reminder.py (chỉ mới thấy
reminder_messages.py là danh sách câu nhắc, không phải file xử
lý lệnh), nên KHÔNG đoán tên hàm Python để tránh gọi sai gây lỗi.
2 nút này hiện hướng dẫn ngắn gọn thay vì tự chạy. Gửi
handlers/reminder.py nếu muốn nâng cấp phần này.
"""

import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from scraper.facebook_scraper import get_latest_posts, FacebookScraperError


def _build_menu_keyboard() -> InlineKeyboardMarkup:
    """Dựng layout nút bấm cho /menu. Sửa ở đây nếu muốn đổi bố cục/nút."""
    keyboard = [
        [InlineKeyboardButton("📰 Xem bài viết", callback_data="menu_baiviet")],
        [
            InlineKeyboardButton("🔔 Bật nhắc nhở", callback_data="menu_nhacnho_bat"),
            InlineKeyboardButton("🔕 Tắt nhắc nhở", callback_data="menu_nhacnho_tat"),
        ],
        [InlineKeyboardButton("⏰ Đặt giờ nhắc", callback_data="menu_setgio")],
        [InlineKeyboardButton("🤖 MCP", callback_data="menu_mcp")],
        [InlineKeyboardButton("« Quay lại menu", callback_data="menu_back")],
    ]
    return InlineKeyboardMarkup(keyboard)


# Layout không có nút "Quay lại" dùng cho tin nhắn menu gốc,
# tránh vòng lặp thừa khi vừa mở /menu lần đầu
def _build_menu_keyboard_root() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📰 Xem bài viết", callback_data="menu_baiviet")],
        [
            InlineKeyboardButton("🔔 Bật nhắc nhở", callback_data="menu_nhacnho_bat"),
            InlineKeyboardButton("🔕 Tắt nhắc nhở", callback_data="menu_nhacnho_tat"),
        ],
        [InlineKeyboardButton("⏰ Đặt giờ nhắc", callback_data="menu_setgio")],
        [InlineKeyboardButton("🤖 MCP", callback_data="menu_mcp")],
    ]
    return InlineKeyboardMarkup(keyboard)


MENU_ROOT_TEXT = "📋 Chọn 1 chức năng bên dưới:"


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xử lý lệnh /menu — gửi tin nhắn kèm bảng nút bấm (tin nhắn MỚI)."""
    await update.message.reply_text(
        MENU_ROOT_TEXT,
        reply_markup=_build_menu_keyboard_root(),
    )


async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Xử lý khi người dùng bấm bất kỳ nút nào trong menu.
    QUY TẮC: luôn answer() ngay đầu tiên để tắt trạng thái loading
    trên máy người dùng ngay lập tức, bất kể phần xử lý bên dưới
    có tốn thời gian hay lỗi hay không.
    """
    query = update.callback_query
    await query.answer()  # tắt loading NGAY, không chờ xử lý xong

    choice = query.data

    try:
        if choice == "menu_baiviet":
            await _handle_baiviet(query)

        elif choice == "menu_nhacnho_bat":
            await query.edit_message_text(
                "🔔 Để bật nhắc nhở, gõ lệnh:\n/nhacnho_bat",
                reply_markup=_back_keyboard(),
            )

        elif choice == "menu_nhacnho_tat":
            await query.edit_message_text(
                "🔕 Để tắt nhắc nhở, gõ lệnh:\n/nhacnho_tat",
                reply_markup=_back_keyboard(),
            )

        elif choice == "menu_setgio":
            await query.edit_message_text(
                "⏰ Để đặt giờ nhắc, gõ lệnh:\n/setgio HH:MM\n\nVí dụ: /setgio 08:00",
                reply_markup=_back_keyboard(),
            )

        elif choice == "menu_mcp":
            await query.edit_message_text(
                "My chưa có làm được !!!   :<",
                reply_markup=_back_keyboard(),
            )

        elif choice == "menu_back":
            await query.edit_message_text(
                MENU_ROOT_TEXT,
                reply_markup=_build_menu_keyboard_root(),
            )

    except Exception as e:
        # Bắt mọi lỗi phát sinh trong lúc edit/xử lý, để KHÔNG BAO GIỜ
        # bot im lặng - luôn có phản hồi cho người dùng biết có sự cố.
        print(f"[menu] Lỗi khi xử lý callback '{choice}': {e}")
        try:
            await query.edit_message_text(f"⚠️ Có lỗi xảy ra: {e}")
        except Exception:
            # Nếu edit cũng lỗi (VD nội dung không đổi), gửi tin nhắn mới thay thế
            await query.message.reply_text(f"⚠️ Có lỗi xảy ra: {e}")


def _back_keyboard() -> InlineKeyboardMarkup:
    """Nút quay lại menu chính, dùng cho các màn hình con."""
    return InlineKeyboardMarkup([[InlineKeyboardButton("« Quay lại menu", callback_data="menu_back")]])


async def _handle_baiviet(query) -> None:
    """
    Xử lý nút "Xem bài viết": sửa tin nhắn hiện trạng thái đang tải
    tại chỗ, cào dữ liệu, rồi sửa lại lần nữa với kết quả cuối.
    """
    await query.edit_message_text("⏳ Đang lấy dữ liệu từ fanpage, vui lòng đợi ít phút...")

    loop = asyncio.get_running_loop()
    try:
        posts = await loop.run_in_executor(None, get_latest_posts, 2, True)
    except FacebookScraperError as e:
        await query.edit_message_text(
            f"⚠️ Không lấy được bài viết.\n\nLý do: {e}",
            reply_markup=_back_keyboard(),
        )
        return
    except Exception as e:
        await query.edit_message_text(
            f"⚠️ Có lỗi không xác định khi cào dữ liệu Facebook:\n{e}",
            reply_markup=_back_keyboard(),
        )
        return

    if not posts:
        await query.edit_message_text(
            "Không tìm thấy bài viết nào mới.",
            reply_markup=_back_keyboard(),
        )
        return

    reply_lines = ["📰 2 bài viết mới nhất từ Trường Đại học Quy Nhơn:\n"]
    for i, post in enumerate(posts, start=1):
        reply_lines.append(f"{i}. {post['text']}\n🔗 {post['url']}\n")

    await query.edit_message_text(
        "\n".join(reply_lines),
        reply_markup=_back_keyboard(),
    )
