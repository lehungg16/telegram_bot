"""
storage.py
Lưu cấu hình nhắc nhở của từng người dùng vào file JSON nhẹ.
Render free không có DB server riêng nên dùng file là đủ cho quy mô cá nhân.

Cấu trúc dữ liệu:
{
  "<chat_id>": {"enabled": true, "time": "21:00"},
  ...
}

LƯU Ý: Render free tier có filesystem KHÔNG bền vững lâu dài giữa các lần
deploy mới (nhưng vẫn giữ được qua các lần "ngủ/thức" và restart thường).
Nếu sau này cần bền vững tuyệt đối qua mỗi lần deploy code mới, cân nhắc
chuyển sang SQLite + Render Disk (trả phí) hoặc 1 DB free bên ngoài.
"""
import json
import os
from typing import Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "reminders.json")

DEFAULT_TIME = "21:00"


def _ensure_file() -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


def load_all() -> dict:
    _ensure_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_all(data: dict) -> None:
    _ensure_file()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(chat_id: int) -> dict:
    data = load_all()
    return data.get(str(chat_id), {"enabled": False, "time": DEFAULT_TIME})


def set_user(chat_id: int, enabled: Optional[bool] = None, time: Optional[str] = None) -> dict:
    """Cập nhật (hoặc tạo mới) cấu hình của 1 người dùng. Chỉ ghi đè field nào được truyền vào."""
    data = load_all()
    current = data.get(str(chat_id), {"enabled": False, "time": DEFAULT_TIME})
    if enabled is not None:
        current["enabled"] = enabled
    if time is not None:
        current["time"] = time
    data[str(chat_id)] = current
    _save_all(data)
    return current
