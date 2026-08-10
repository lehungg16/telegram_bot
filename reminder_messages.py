"""
reminder_messages.py
Mẫu nội dung nhắc nhở sức khỏe — mỗi lần gửi sẽ chọn ngẫu nhiên 1 câu.
"""
import random

REMINDER_MESSAGES = [
    "💧 Nhớ uống 1 cốc nước nhé, đừng để khát mới uống!",
    "🧘 Đứng dậy vươn vai, đi lại vài bước cho đỡ mỏi nào.",
    "👀 Nghỉ mắt 20 giây — nhìn ra xa 20 feet (~6m) theo quy tắc 20-20-20.",
    "🌙 Sắp đến giờ rồi đó, chuẩn bị đi ngủ đúng giờ để mai khỏe nhé!",
    "🚶 Ngồi lâu rồi đấy, đứng dậy đi bộ nhẹ 2-3 phút thôi.",
    "🫁 Hít thở sâu vài nhịp, thả lỏng vai và cổ một chút nào.",
    "🍎 Đã đến giờ rồi, đừng quên ăn uống đúng bữa nhé.",
]


def get_random_message() -> str:
    return random.choice(REMINDER_MESSAGES)
