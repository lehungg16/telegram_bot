"""
handlers/commands.py
---------------------
Nơi DUY NHẤT khai báo toàn bộ danh sách lệnh của bot.
/help và register_commands.py đều đọc danh sách từ đây.

GHI CHÚ MERGE: đây là file MẪU đã bổ sung lệnh của Giai đoạn 3.
Hãy đối chiếu với file commands.py thật của bạn (đã có sẵn lệnh
/start, /help, /nhacnho_bat, /nhacnho_tat, /setgio từ Giai đoạn
1-2) và CHỈ THÊM dòng "baiviet" vào cuối danh sách - không xóa
các dòng đã có.
"""

COMMANDS = [
    ("start", "Bắt đầu sử dụng bot"),
    ("help", "Xem danh sách lệnh"),
    ("nhacnho_bat", "Bật nhắc nhở sức khỏe định kỳ"),
    ("nhacnho_tat", "Tắt nhắc nhở sức khỏe"),
    ("setgio", "Đặt giờ nhắc nhở, VD: /setgio 14:30"),
    ("baiviet", "Xem 2 bài viết mới nhất từ fanpage Trường ĐH Quy Nhơn"),
]
