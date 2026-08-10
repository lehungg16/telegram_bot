"""
facebook_scraper.py
--------------------
Dùng Selenium mở fanpage CÔNG KHAI của Trường Đại học Quy Nhơn
(https://www.facebook.com/daihocquynhon) mà KHÔNG đăng nhập bất kỳ
tài khoản nào, lấy N bài viết mới nhất (nội dung text + link).

Vì sao đổi sang không đăng nhập:
- Đăng nhập bằng acc clone qua Selenium bị Facebook yêu cầu giải
  captcha, không thể tự động hóa hợp lệ và an toàn.
- Fanpage là trang công khai, nội dung bài viết xem được mà không
  cần tài khoản -> bỏ hẳn bước đăng nhập, giảm rủi ro khóa acc,
  đơn giản hóa code.

HẠN CHẾ cần biết trước:
- Khi chưa đăng nhập, Facebook có thể giới hạn số bài xem được
  (đôi khi chỉ hiện 1-2 bài đầu rồi che phần còn lại, mời đăng
  nhập để xem thêm). Vì chỉ cần 2 bài mới nhất nên thường vẫn đủ,
  nhưng nếu Facebook thắt chặt hơn trong tương lai, hàm này có
  thể trả về ít hơn 2 bài hoặc báo lỗi.
- Facebook có thể yêu cầu xác nhận "You must log in to continue"
  ngay khi vừa vào trang -> script sẽ phát hiện và báo lỗi rõ
  ràng thay vì treo im lặng.
"""

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

FANPAGE_URL = "https://www.facebook.com/daihocquynhon"

# Selector có thể thay đổi bất cứ lúc nào vì Facebook liên tục
# đổi giao diện / class name random. Đây là điểm DỄ GÃY NHẤT
# của toàn bộ Giai đoạn 3 - nếu sau này không cào được nữa,
# đây là nơi đầu tiên cần kiểm tra lại.
POST_CONTAINER_XPATH = "//div[@role='article']"


class FacebookScraperError(Exception):
    """Lỗi tùy chỉnh để handler Telegram bắt và báo về cho người dùng."""
    pass


def _build_driver(headless: bool = False):
    """
    Tạo Chrome driver.
    headless=False (mặc định) để bạn thấy được trình duyệt khi
    debug lần đầu. Khi deploy lên Render ở Giai đoạn 5 sẽ cần
    đổi thành headless=True.
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--lang=vi-VN")
    # Giả lập user-agent trình duyệt thật
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    return driver


def _check_login_wall(driver):
    """
    Kiểm tra xem Facebook có chặn xem trang bằng cách bắt đăng
    nhập không. Nếu có -> báo lỗi rõ ràng thay vì im lặng trả
    về danh sách rỗng.
    """
    current_url = driver.current_url.lower()
    page_source_lower = driver.page_source.lower()

    if "login" in current_url or "checkpoint" in current_url:
        raise FacebookScraperError(
            "Facebook chuyển hướng sang trang đăng nhập khi vào fanpage "
            "(không cho xem ẩn danh lúc này). Có thể do quá nhiều lượt "
            "truy cập ẩn danh liên tiếp bị nghi ngờ, hoặc Facebook siết "
            "chặt hơn với IP/trình duyệt hiện tại."
        )
    if "you must log in" in page_source_lower or "log in to continue" in page_source_lower:
        raise FacebookScraperError(
            "Facebook yêu cầu đăng nhập mới cho xem nội dung fanpage này "
            "vào lúc này."
        )


# Các dòng "rác" giao diện Facebook hay lẫn vào el.text, cần lọc bỏ.
# So khớp theo kiểu "dòng bắt đầu bằng" hoặc "dòng chỉ chứa đúng từ này",
# vì nội dung caption thật hiếm khi trùng khớp y hệt các cụm này.
_NOISE_EXACT_LINES = {
    "thích", "bình luận", "chia sẻ", "xem thêm", "xem chi tiết",
    "tất cả cảm xúc:", "gỡ theo dõi", "theo dõi",
}
_NOISE_PREFIXES = (
    "tất cả cảm xúc",
)
_PAGE_NAME = "QNU - Trường Đại học Quy Nhơn"


def _is_noise_line(line: str) -> bool:
    """Nhận diện 1 dòng có phải rác giao diện (thời gian, nút bấm, số liệu) không."""
    stripped = line.strip()
    if not stripped:
        return True
    if stripped == _PAGE_NAME:
        return True
    # Dòng chỉ chứa đúng chữ viết tắt tên trang (VD: "QNU") - thường là
    # phần dư thừa còn sót lại quanh nút "Xem thêm" khi caption bị cắt
    # ngắn ở giao diện chưa đăng nhập.
    page_short_name = _PAGE_NAME.split(" - ")[0].strip()
    if stripped == page_short_name:
        return True
    lower = stripped.lower()
    if lower in _NOISE_EXACT_LINES:
        return True
    if lower.startswith(_NOISE_PREFIXES):
        return True
    # Dòng chỉ có số/dấu chấm/dấu phẩy (VD: "279", "1,2K", "6", "5") -> số lượt cảm xúc/bình luận
    if all(c.isdigit() or c in ",.KkMm " for c in stripped) and any(c.isdigit() for c in stripped):
        return True
    # Dòng dạng thời gian đăng bài kiểu "17 giờ", "2 ngày", "·"
    if stripped == "·":
        return True
    time_units = ("giờ", "phút", "ngày", "tuần", "tháng", "năm")
    words = stripped.split()
    if len(words) <= 2 and words and words[0].isdigit() and any(u in lower for u in time_units):
        return True
    return False


def _clean_post_text(raw_text: str) -> str:
    """Lọc bỏ các dòng rác, chỉ giữ lại nội dung caption thật của bài viết."""
    lines = raw_text.split("\n")
    kept = [line.strip() for line in lines if not _is_noise_line(line)]
    return "\n".join(kept).strip()


def _clean_url(href: str) -> str:
    """
    Làm sạch link bài viết:
    - Cắt bỏ query string (?...)
    - Facebook hay chèn ký tự control ẩn \\ufffc ngay trước 1 số rác ở
      cuối href (dấu vết icon ẩn trong link) -> cắt đứt tại vị trí xuất
      hiện \\ufffc ĐẦU TIÊN, không chỉ xóa mỗi ký tự đó, để không dính
      rác còn sót lại phía sau nó.
    """
    cleaned = href.split("?")[0]
    if "\ufffc" in cleaned:
        cleaned = cleaned.split("\ufffc")[0]
    return cleaned.strip()


def _extract_posts(driver, limit: int = 2):
    """
    Vào fanpage (không đăng nhập) và lấy ra `limit` bài viết mới nhất.
    Mỗi bài trả về dạng dict: {"text": ..., "url": ...}
    """
    driver.get(FANPAGE_URL)
    time.sleep(4)

    _check_login_wall(driver)

    wait = WebDriverWait(driver, 20)
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, POST_CONTAINER_XPATH)))
    except TimeoutException:
        raise FacebookScraperError(
            "Không tải được bài viết nào từ fanpage sau 20 giây. Có thể "
            "Facebook đã đổi giao diện, hoặc chặn xem ẩn danh vào lúc này. "
            "Thử lại sau, hoặc cân nhắc quay lại phương án đăng nhập bằng "
            "cookie thật nếu tình trạng này lặp lại thường xuyên."
        )

    # Cuộn trang xuống một chút để đảm bảo đủ bài viết được render ra DOM
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
    time.sleep(3)

    post_elements = driver.find_elements(By.XPATH, POST_CONTAINER_XPATH)

    posts = []
    for el in post_elements:
        if len(posts) >= limit:
            break
        try:
            raw_text = el.text.strip()
            if not raw_text:
                continue  # Bỏ qua bài không có nội dung text (chỉ ảnh/video)

            text = _clean_post_text(raw_text)
            if not text:
                continue  # Sau khi lọc rác mà rỗng -> bỏ qua, không phải bài có nội dung

            # Tìm link bài viết: chỉ lấy href có /posts/ (link bài viết chính,
            # không lấy link ảnh/reaction/comment lẫn trong cùng khối)
            link = None
            anchors = el.find_elements(By.TAG_NAME, "a")
            for a in anchors:
                href = a.get_attribute("href") or ""
                if "/posts/" in href:
                    link = _clean_url(href)
                    break
            if not link:
                # Không có link /posts/ -> thử các dạng khác (ảnh/video)
                for a in anchors:
                    href = a.get_attribute("href") or ""
                    if "/photo" in href or "/videos/" in href or "story_fbid" in href:
                        link = _clean_url(href)
                        break

            posts.append({
                "text": text[:500],  # Giới hạn độ dài để không tràn tin nhắn Telegram
                "url": link or FANPAGE_URL,
            })
        except Exception as e:
            print(f"[facebook_scraper] Bỏ qua 1 bài lỗi khi parse: {e}")
            continue

    if not posts:
        raise FacebookScraperError(
            "Tìm thấy khung bài viết nhưng không lấy được nội dung nào "
            "(có thể Facebook đang che nội dung vì chưa đăng nhập, hoặc "
            "cấu trúc trang đã thay đổi)."
        )

    return posts


def get_latest_posts(limit: int = 2, headless: bool = False):
    """
    Hàm chính để handler Telegram gọi.
    Trả về list các dict {"text":.., "url":..}, ném FacebookScraperError
    nếu có lỗi (để handler bắt và báo qua Telegram).
    KHÔNG đăng nhập bất kỳ tài khoản nào - chỉ xem nội dung công khai.
    """
    driver = _build_driver(headless=headless)
    try:
        posts = _extract_posts(driver, limit=limit)
        return posts
    finally:
        driver.quit()
