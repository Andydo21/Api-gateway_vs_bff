# 🔄 Giải Thích Các Luồng Hoạt Động Trong Dự Án (Project Flows)

Hệ thống của bạn được xây dựng trên kiến trúc **Microservices** hiện đại, kết hợp với **API Gateway**, **BFF (Backend for Frontend)**, và mô hình **Event-driven** (hướng sự kiện). Dưới đây là giải thích chi tiết các luồng chính:

---

## Luồng Xử lý & Kiến trúc Proxy/BFF

Dưới đây là giải giải thích về cách dữ liệu di chuyển trong hệ thống và tại sao chúng ta cần các thành phần như API Gateway (Proxy) và BFF.

### 1. Proxy (API Gateway) là gì? Tại sao phải thêm vào?

Hãy tưởng tượng hệ thống Microservices của bạn giống như một tòa nhà văn phòng lớn với nhiều phòng ban (User Service, Startup Service, v.v.).

**Nếu không có Proxy:**
Khách hàng (Frontend) muốn giao dịch với 10 phòng ban thì phải tự đi tìm đúng cửa của 10 phòng đó. Nếu phòng ban chuyển chỗ, khách hàng sẽ bị lạc.

**Khi có Proxy (Apache APISIX):**
Proxy đóng vai trò như **Quầy lễ tân** duy nhất ở cổng chính.
- **Một địa chỉ duy nhất:** Frontend chỉ cần gửi yêu cầu đến `http://localhost/`. Lễ tân sẽ biết phải dẫn khách đến đúng phòng nào.
- **Bảo vệ (Security):** Lễ tân kiểm tra thẻ căn cước (JWT Token) của khách ngay tại cửa. Nếu không có thẻ, khách bị đuổi về luôn, không được vào quấy rầy các phòng ban bên trong.
- **Kiểm soát (Rate Limit):** Ngăn chặn một người chạy ra chạy vào quá nhiều lần làm tắc nghẽn cổng.
- **Theo dõi (Logging):** Ghi lại nhật ký ai đã vào tòa nhà vào lúc nào.

### 2. BFF (Backend-for-Frontend) khác gì Proxy?

Nếu Proxy là **Lễ tân**, thì BFF giống như một **Trợ lý riêng** của từng nhóm khách.

- **Proxy (APISIX):** Chỉ dẫn đường và kiểm tra an ninh (Cấp độ hạ tầng).
- **BFF (Admin BFF / Web BFF):** Hiểu rõ khách cần gì. Nếu khách muốn một bản "Báo cáo tổng hợp", trợ lý (BFF) sẽ đi gom dữ liệu từ 3-4 phòng ban khác nhau, đóng gói thành một tệp duy nhất và đưa cho khách. Khách không phải tự đi gom (Aggregation).

---

## 3. Luồng Truy Vấn Dữ Liệu (Synchronous Request Flow)
**Mục đích:** Khi người dùng muốn xem thông tin (VD: danh sách Startup, xem hồ sơ cá nhân).

*   **Bước 1 (Frontend):** Trình duyệt gửi request (VD: `GET /web/startups/`) tới **API Gateway** (Port 8000).
*   **Bước 2 (API Gateway):**
    *   Kiểm tra đăng nhập (JWT Token).
    *   Nếu hợp lệ, nó sẽ đính kèm thông tin User ID vào Header (`X-User-ID`) và chuyển tiếp tới **Web-BFF**.
*   **Bước 3 (Web-BFF):** 
    *   Nó đóng vai trò "người tổng hợp". Nó sẽ gọi song song nhiều Microservices (VD: Startup Service để lấy thông tin công ty, User Service để lấy thông tin chủ sở hữu).
    *   Nó có thể lưu kết quả vào **Redis Cache** để lần sau tải nhanh hơn.
*   **Bước 4 (Microservices):** Trả dữ liệu về cho BFF. BFF gộp lại và trả về cho Frontend một bản duy nhất đã được tối ưu.

---

## 2. Luồng Xử Lý Giao Dịch Tin Cậy (Transactional Outbox Flow)
**Mục đích:** Đảm bảo khi lưu dữ liệu vào Database thì sự kiện tương ứng chắc chắn sẽ được gửi đi (VD: Khi đặt chỗ thành công, chắc chắn phải có thông báo).

*   **Bước 1:** Microservice (VD: `booking-service`) thực hiện lưu một bản ghi mới (VD: `PitchBooking`) vào Database.
*   **Bước 2:** Trong cùng một giao dịch (transaction) đó, nó lưu thêm một bản ghi vào bảng `outbox_events`.
*   **Bước 3 (Outbox Processor):** Một tiến trình chạy ngầm (`run_outbox_processor.py`) quét liên tục bảng `outbox_events`. 
*   **Bước 4:** Khi thấy sự kiện mới, nó đẩy sự kiện đó vào **Kafka** và đánh dấu là đã xử lý (`processed=True`). 
    *   *Tại sao làm vậy?* Để tránh trường hợp lưu DB thành công nhưng gửi Kafka thất bại (làm mất dữ liệu).

---

## 3. Luồng Sự Kiện Bất Đồng Bộ (Asynchronous Event Flow - Kafka)
**Mục đích:** Các dịch vụ thông báo cho nhau mà không cần chờ đợi nhau.

*   **Bên gửi (Producer):** Một dịch vụ (VD: `funding-service`) đẩy sự kiện `payment_completed` vào Kafka.
*   **Bên nhận (Consumer):** 
    *   **Notification Service:** Nghe sự kiện này để gửi tin nhắn chúc mừng cho người dùng qua WebSocket.
    *   **Matchmaking Service:** Nghe sự kiện này để tính toán lại điểm gợi ý (vì người dùng đã quan tâm/đầu tư).
*   **Lợi ích:** Hệ thống chạy rất nhanh vì `funding-service` không cần đợi `notification-service` làm việc xong.

---

## 4. Luồng Thông Báo Real-time (WebSocket Flow)
**Mục đích:** Cập nhật thông báo tức thời cho người dùng mà không cần reload trang.

*   **Bước 1:** `notification-service` nhận được sự kiện từ Kafka.
*   **Bước 2:** Nó tìm xem người dùng đó có đang online không thông qua **Django Channels**.
*   **Bước 3:** Nó đẩy thông báo trực tiếp xuống trình duyệt qua kết nối **WebSocket**. Người dùng sẽ thấy một popup thông báo ngay lập tức.

---

## 5. Các Luồng Nghiệp Vụ Chính (Business Flows)

### A. Luồng Đặt Lịch Pitching (Pitch Booking Flow)
1.  **User** chọn khung giờ trống từ `scheduling-service`.
2.  **BFF** gọi `booking-service` để tạo yêu cầu đặt lịch.
3.  **Booking Service** lưu vào DB và Outbox.
4.  **Kafka** nhận sự kiện `pitch_booking_created`.
5.  **Notification Service** gửi báo xác nhận cho User.
6.  **Meeting Service** (Consumer) tự động tạo link Zoom/Google Meet cho buổi pitch đó.

### B. Luồng Thanh Toán (Payment Flow)
1.  **User** thực hiện thanh toán qua `funding-service`.
2.  Sau khi thanh toán thành công, sự kiện `payment_completed` được bắn vào Kafka.
3.  **Booking Service** cập nhật trạng thái đơn hàng.
4.  **Portfolio Service** (nếu có) cập nhật danh mục đầu tư.

---

## 💡 Tại sao phải chia nhiều luồng như vậy?
-   **Tách biệt (Isolation):** Nếu dịch vụ Thông báo bị hỏng, người dùng vẫn có thể Đặt lịch bình thường.
-   **Mở rộng (Scalability):** Bạn có thể chạy 10 máy chủ cho dịch vụ Startup nhưng chỉ cần 1 máy chủ cho dịch vụ Feedback.
-   **Tốc độ (Speed):** Nhờ Caching (Redis) và Async (Kafka), trải nghiệm người dùng sẽ cực kỳ mượt mà.
