"""
handlers/commands.py
Danh sách lệnh tập trung một chỗ — dùng cho:
1. Lệnh /help (liệt kê cho người dùng)
2. Đăng ký menu "/" với BotFather (xem register_commands.py)

Khi thêm lệnh mới ở Giai đoạn 2, 3... chỉ cần thêm 1 dòng vào đây,
cả /help và menu BotFather sẽ tự cập nhật theo.
"""

COMMANDS = [
    ("start", "Bắt đầu / xem lời chào"),
    ("help", "Xem danh sách lệnh"),
    # Giai đoạn 2 sẽ thêm:
    # ("nhacnho_bat", "Bật nhắc nhở sức khỏe định kỳ"),
    # ("nhacnho_tat", "Tắt nhắc nhở sức khỏe"),
    # ("setgio", "Đặt giờ nhắc — cú pháp: /setgio HH:MM"),
    # Giai đoạn 3 sẽ thêm:
    # ("baiviet", "Lấy bài viết mới nhất từ group Facebook"),
]
