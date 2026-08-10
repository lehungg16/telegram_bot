"""
handlers/baiviet.py
--------------------
Xử lý lệnh /baiviet: lấy 2 bài viết mới nhất từ fanpage
Trường Đại học Quy Nhơn (https://www.facebook.com/daihocquynhon)
bằng acc clone, gửi lại nội dung + link qua Telegram.

Vì Selenium là code ĐỒNG BỘ (chạy tuần tự, không async), còn bot
Telegram chạy theo kiểu async - nếu gọi thẳng Selenium trong hàm
handler async thì cả bot sẽ bị "đứng hình", không phản hồi được
lệnh nào khác trong lúc đang cào. Giải pháp: chạy Selenium trong
1 thread riêng (run_in_executor), để bot vẫn xử lý được các tin
nhắn/lệnh khác song song.
"""

import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from scraper.facebook_scraper import get_latest_posts, FacebookScraperError

SO_BAI_MOI_NHAT = 2


async def baiviet_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Báo ngay cho người dùng biết bot đang xử lý, vì Selenium cào
    # mất vài chục giây chứ không phản hồi tức thì
    status_message = await update.message.reply_text(
        "Đang lấy dữ liệu từ fanpage, vui lòng đợi ít phút..."
    )

    loop = asyncio.get_running_loop()
    try:
        # Chạy hàm đồng bộ get_latest_posts trong 1 thread riêng,
        # không làm nghẽn event loop chính của bot
        posts = await loop.run_in_executor(
            None, get_latest_posts, SO_BAI_MOI_NHAT, False
        )
    except FacebookScraperError as e:
        await status_message.edit_text(
            f"⚠️ Không lấy được bài viết.\n\nLý do: {e}"
        )
        return
    except Exception as e:
        # Bắt mọi lỗi không lường trước (VD: Chrome chưa cài, ChromeDriver lỗi...)
        # để bot KHÔNG bao giờ im lặng khi gặp sự cố
        await status_message.edit_text(
            f"⚠️ Có lỗi không xác định khi cào dữ liệu Facebook:\n{e}"
        )
        return

    if not posts:
        await status_message.edit_text("Không tìm thấy bài viết nào mới.")
        return

    reply_lines = [f"📰 {SO_BAI_MOI_NHAT} bài viết mới nhất từ Trường Đại học Quy Nhơn:\n"]
    for i, post in enumerate(posts, start=1):
        reply_lines.append(f"{i}. {post['text']}\n🔗 {post['url']}\n")

    await status_message.edit_text("\n".join(reply_lines))
