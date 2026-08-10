"""
utils/time_utils.py
Parse và kiểm tra chuỗi giờ do người dùng nhập, dạng "HH:MM" (24h).
"""
import re
from datetime import time as dt_time
from typing import Optional
from zoneinfo import ZoneInfo

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")

_TIME_PATTERN = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def parse_hhmm(text: str) -> Optional[dt_time]:
    """Trả về datetime.time (kèm timezone VN) nếu hợp lệ, None nếu sai định dạng."""
    match = _TIME_PATTERN.match(text.strip())
    if not match:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    return dt_time(hour=hour, minute=minute, tzinfo=VN_TZ)
