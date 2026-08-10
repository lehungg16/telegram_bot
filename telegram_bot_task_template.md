# TEMPLATE CÔNG VIỆC — BOT TELEGRAM ĐA CHỨC NĂNG

**Phạm vi đã chốt:** 3 chức năng chính (menu lệnh, nhắc nhở sức khỏe, lấy tin group Facebook bằng acc clone). Chức năng "AI điều khiển máy tính cá nhân" tạm gác lại, chỉ ghi chú hướng đi cho sau này.

**Ngôn ngữ:** Python — vì có thư viện `python-telegram-bot` mạnh, dễ deploy free, dễ ghép Selenium.
**Hosting:** Render.com (free Web Service).
x là đã làm
---

## GIAI ĐOẠN 0 — Chuẩn bị môi trường
- [X] Tạo bot qua **@BotFather** trên Telegram, lấy `TOKEN`
- [X] Tạo tài khoản Render.com (free), liên kết với GitHub
- [x] Tạo repo Git riêng cho bot, cài Python 3.14+
- [x] Cài thư viện: `python-telegram-bot`, `APScheduler`, `selenium`, `python-dotenv`, `Flask` (hoặc `fastapi`, cần cho webhook)
- [x] Tạo file `.env` chứa TOKEN — **không** đưa lên GitHub public (thêm vào `.gitignore`)

## GIAI ĐOẠN 1 — Khung bot & Menu lệnh (`/command`)
- [ ] Viết `main.py` khởi tạo bot, kết nối Telegram Bot API
- [ ] Đăng ký danh sách lệnh với BotFather (`/setcommands`) để hiện menu `/` khi gõ
- [ ] Lệnh `/start` — chào mừng, hướng dẫn sơ lược cách dùng
- [ ] Lệnh `/help` — liệt kê toàn bộ lệnh kèm mô tả ngắn
- [ ] Tách code theo từng handler riêng cho mỗi lệnh (để dễ thêm chức năng sau)
- [ ] Chạy thử ở máy local, xác nhận bot phản hồi đúng trước khi deploy

## GIAI ĐOẠN 2 — Nhắc nhở sức khỏe
- [ ] Lệnh `/nhacnho_bat` — bật nhắc nhở định kỳ
- [ ] Lệnh `/nhacnho_tat` — tắt nhắc nhở
- [ ] Lệnh `/setgio HH:MM` — người dùng tự đặt giờ nhắc (uống nước, đứng dậy, ngủ đúng giờ...)
- [ ] Dùng `APScheduler` (hoặc JobQueue có sẵn trong thư viện) để lên lịch gửi tin theo giờ đã đặt
- [ ] Lưu cấu hình nhắc nhở của người dùng vào file JSON hoặc SQLite (free không có DB server riêng nên dùng file nhẹ)
- [ ] Soạn sẵn vài mẫu nội dung nhắc (uống nước, giãn cơ, nghỉ mắt, đi ngủ)
- [ ] Test: bot gửi tin đúng giờ đã hẹn, kể cả sau khi Render khởi động lại

## GIAI ĐOẠN 3 — Lấy tin từ Group Facebook (dùng acc clone)
> Facebook không cho bot đọc bài viết trong group qua API chính thức, kể cả group riêng của bạn — nên cách khả thi duy nhất là dùng trình duyệt tự động (Selenium) đăng nhập bằng tài khoản thật.

- [ ] Chọn 1 acc clone cố định riêng cho việc này (đã có sẵn theo bạn nói) — không dùng acc chính, tách theo từng group/nơi để không trùng
- [ ] Cài Selenium + ChromeDriver (chạy chế độ headless trên server)
- [ ] Viết script đăng nhập Facebook bằng acc clone, **lưu cookie sau lần đăng nhập đầu** để không phải đăng nhập lại nhiều lần (đăng nhập lại liên tục dễ khiến Facebook nghi ngờ và khóa acc)
- [ ] Viết script vào group, lấy tiêu đề + link của N bài viết mới nhất
- [ ] Lệnh `/baiviet` — gửi danh sách bài viết mới nhất từ group
- [ ] (Tuỳ chọn) Lên lịch tự cào định kỳ (vd mỗi 3 tiếng) và tự nhắn khi có bài mới
- [ ] Xử lý lỗi: Facebook đổi giao diện / hiện captcha / yêu cầu xác minh 2 lớp → script phải báo lỗi qua Telegram cho bạn biết, không được im lặng
- **Lưu ý rủi ro:** đăng nhập tự động lặp lại là hành vi trái Điều khoản dịch vụ của Facebook, acc clone có thể bị khoá tạm thời hoặc vĩnh viễn tuỳ tần suất chạy — nên set tần suất cào thưa (không quá 1 lần/giờ) để giảm rủi ro

## GIAI ĐOẠN 4 — (Để dành tương lai) Kết nối AI điều khiển máy tính cá nhân
*Đã quyết định bỏ qua ở bản này. Ghi chú lại hướng đi cho khi bạn sẵn sàng:*
- [ ] Cần 1 script/agent nhỏ chạy liên tục **trên chính máy tính cá nhân** (Render không thể chạm vào máy bạn)
- [ ] Bot gửi lệnh → agent trên máy nhận lệnh (qua polling riêng hoặc 1 API trung gian) → agent thực thi lệnh hệ thống (mở trình duyệt, mở app...)
- [ ] Có thể tích hợp AI (Claude/OpenAI API) để agent hiểu lệnh tự nhiên rồi map ra hành động cụ thể
- [ ] Cân nhắc bảo mật: agent chạy lệnh hệ thống trên máy cá nhân — nếu lộ token, người khác có thể điều khiển máy bạn

## GIAI ĐOẠN 5 — Deploy lên Render.com (Free)
- [ ] Push code lên GitHub
- [ ] Tạo "Web Service" mới trên Render, kết nối repo
- [ ] Set biến môi trường `TELEGRAM_TOKEN` (và acc Facebook nếu cần) trong mục Environment của Render — không hardcode trong code
- [ ] Chuyển bot sang chế độ **Webhook** thay vì polling — Render free chỉ giữ service thức khi có request đến, polling gần như chắc chắn bị cho ngủ
- [ ] Thêm route `/health` trả về `200 OK` để Render healthcheck không hiểu nhầm là lỗi rồi restart
- [ ] Dùng dịch vụ ping ngoài miễn phí (UptimeRobot hoặc cron-job.org) gọi vào bot mỗi 10–14 phút để giữ service không ngủ — **quan trọng** vì nếu ngủ thì lịch nhắc sức khỏe và lịch cào Facebook sẽ không tự chạy đúng giờ
- [ ] Test lại toàn bộ 3 chức năng sau khi deploy thật

---

## Lưu ý chung
- Render free tier tự ngủ sau ~15 phút không có request — đây là lý do bắt buộc phải dùng webhook + ping ngoài, không dùng polling
- Tuyệt đối không đưa TOKEN bot hay thông tin đăng nhập Facebook lên GitHub public
- Thứ tự làm khuyến nghị: **Giai đoạn 1 → 2 → 5 (deploy sớm để test thật)** rồi mới làm **Giai đoạn 3** (khó và rủi ro hơn, nên làm sau khi phần lõi đã chạy ổn)
