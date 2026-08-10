"""
config.py
Đọc cấu hình từ file .env (local) hoặc biến môi trường (Render).
"""
import os
from dotenv import load_dotenv

# Load file .env nếu chạy local. Trên Render, biến môi trường
# đã được set sẵn trong mục Environment nên load_dotenv() sẽ
# không tìm thấy file .env và không làm gì cả (không lỗi).
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise RuntimeError(
        "hoặc set biến môi trường TELEGRAM_TOKEN."
    )
