# Database Tables Overview

Dựa trên cấu trúc dự án microservices của bạn, dưới đây là danh sách toàn bộ các bảng dữ liệu được định nghĩa trong các `models.py`.

> [!NOTE]
> Dự án của bạn hiện đang cấu hình sử dụng **PostgreSQL** (theo `docker-compose.yml` và `settings.py`). Tuy nhiên, tôi vẫn cung cấp các lệnh MySQL như bạn yêu cầu, cùng với các lệnh PostgreSQL tương ứng để bạn có thể truy vấn chính xác.

## 1. Lệnh xem danh sách Table

| Database | Lệnh xem tất cả các bảng | Lệnh xem cấu trúc 1 bảng |
| :--- | :--- | :--- |
| **MySQL** | `SHOW TABLES;` | `DESCRIBE <tên_bảng>;` |
| **PostgreSQL** | `\dt` hoặc `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';` | `\d <tên_bảng>` |

---

## 2. Danh sách các bảng theo Microservice

Dưới đây là các bảng (table) chính được tạo từ code Django:

### 👤 User Service
- `users`: Thông tin người dùng (Admin, Investor, User)
- `user_outbox_events`: Lưu trữ sự kiện để đồng bộ dữ liệu (Transactional Outbox Pattern)

### 🚀 Startup Service
- `startups`: Thông tin về các công ty startup
- `startup_categories`: Danh mục ngành nghề của startup
- `investors`: Hồ sơ thông tin nhà đầu tư
- `reviews`: Đánh giá của người dùng về startup
- `startup_outbox_events`: Sự kiện của startup service

### 📅 Scheduling & Booking Services
- `pitch_requests`: Yêu cầu pitching của startup
- `pitch_slots`: Các khung giờ trống của nhà đầu tư
- `availability_templates`: Mẫu thời gian rảnh định kỳ
- `pitch_bookings`: Thông tin đặt chỗ pitching thành công
- `waitlists`: Danh sách chờ khi khung giờ đã đầy
- `pitch_booking_history`: Lịch sử thay đổi (đổi lịch, hủy lịch)
- `scheduling_outbox_events` / `booking_outbox_events`: Sự kiện liên quan

### 💰 Funding & Feedback Services
- `payments`: Thông tin giao dịch thanh toán
- `feedbacks`: Phản hồi sau buổi pitch
- `investment_interests`: Mức độ quan tâm đầu tư
- `funding_outbox_events` / `feedback_outbox_events`: Sự kiện liên quan

### 🛠 Resource & Matchmaking Services
- `event_resources`: Tài nguyên sự kiện (gian hàng, thiết bị)
- `resource_reservations`: Thông tin đặt trước tài nguyên
- `user_interactions`: Lịch sử tương tác của người dùng (view, click, like)
- `startup_similarities`: Dữ liệu gợi ý startup tương đồng (Recommendation System)
- `resource_outbox_events` / `matchmaking_outbox_events`: Sự kiện liên quan

### 🔔 Notification & Meeting Services
- `notifications`: Thông báo cho người dùng
- `meetings`: Thông tin phòng họp online (Zoom, Google Meet)
- `meeting_outbox_events`: Sự kiện liên quan

---

## 4. Lệnh Import vào MySQL

Nếu bạn đã có file SQL (ví dụ: `schema.sql`) và muốn import vào MySQL, hãy sử dụng lệnh sau trong Terminal/Command Prompt:

```bash
# Cú pháp tổng quát
mysql -u [username] -p [database_name] < [path/to/your_file.sql]

# Ví dụ với người dùng root và database 'microservices'
mysql -u root -p microservices < schema.sql
```

### Cách tạo Schema cho MySQL từ Django
Vì dự án của bạn dùng Django, cách tốt nhất để có lệnh SQL chuẩn MySQL là:
1. Sửa `ENGINE` trong `settings.py` thành `'django.db.backends.mysql'`.
2. Chạy lệnh sau để lấy câu lệnh SQL mà không cần chạy vào DB:
```bash
python manage.py sqlmigrate api 0001
```

---

## 5. Các Luồng Mới Đã Được Bổ Sung (Enhanced Flows)

Tôi đã bổ sung thêm các luồng nghiệp vụ quan trọng vào code để dự án vận hành mượt mà hơn:

### ⚙️ Luồng Phê Duyệt Pitch (Manual)
- **Cơ chế:** Admin hoặc Investor có thể phê duyệt/từ chối yêu cầu của Startup.
- **API (BFF):** 
    - `POST /web/pitch/{id}/approve/`
    - `POST /web/pitch/{id}/reject/`
- **Tác động:** Khi APPROVE, một sự kiện Kafka sẽ được bắn đi để các service khác biết.

### 🤖 Luồng Tự Động Tạo Meeting (Automated)
- **Cơ chế:** Ngay khi một Booking được xác nhận (`pitch_booking_created`), service **Meeting** sẽ tự động bắt sự kiện và tạo một phòng họp Zoom ảo.
- **Code:** Xem tại `meeting-service/api/management/commands/run_kafka_consumer.py`.

### 📈 Luồng Theo Dõi Mối Quan Tâm (Investor Interest)
- **Cơ chế:** Khi Investor đánh giá "INTERESTED", hệ thống sẽ lưu vào Outbox để chuẩn bị gửi thông báo cho Startup và tính toán Matchmaking.

---

- **Apache APISIX Gateway Integration**:
    - **Infrastructure**: Added `apisix` and `etcd` services.
    - **Dynamic Routing**: Replaced static Nginx with APISIX for flexible traffic management.
    - **Observability**: Built-in `prometheus` and `prometheus` metrics support.
    - **Entry Points**: 
        - Port 80: Client Gateway.
        - Port 9180: Admin API.
        - Port 9091: Metrics.

---

## 6. Tài liệu Quy trình chi tiết từng Microservice (Per-Service Flows)

Để bạn dễ dàng quản lý và mở rộng hệ thống, tôi đã chia nhỏ tài liệu quy trình cho từng Microservice:

*   👤 **[User Service](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/service_flows/user_service.md)**
*   🚀 **[Startup Service](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/service_flows/startup_service.md)**
*   📅 **[Scheduling Service](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/service_flows/scheduling_service.md)**
*   📝 **[Booking Service](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/service_flows/booking_service.md)**
*   💰 **[Funding Service](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/service_flows/funding_service.md)**
*   💬 **[Feedback Service](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/service_flows/feedback_service.md)**
*   📦 **[Resource Service](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/service_flows/resource_service.md)**
*   🔍 **[Matchmaking Service](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/service_flows/matchmaking_service.md)**
*   🤝 **[Meeting Service](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/service_flows/meeting_service.md)**
*   🔔 **[Notification Service](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/service_flows/notification_service.md)**

---

> [!TIP]
> **Danh sách các file SQL Schema riêng biệt cho từng Microservice:**
>
> 1.  👤 **[user_service.sql](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/schemas/user_service.sql)**
> 2.  🚀 **[startup_service.sql](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/schemas/startup_service.sql)**
> 3.  📅 **[scheduling_service.sql](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/schemas/scheduling_service.sql)**
> 4.  📝 **[booking_service.sql](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/schemas/booking_service.sql)**
> 5.  💰 **[funding_service.sql](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/schemas/funding_service.sql)**
> 6.  💬 **[feedback_service.sql](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/schemas/feedback_service.sql)**
> 7.  📦 **[resource_service.sql](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/schemas/resource_service.sql)**
> 8.  🔍 **[matchmaking_service.sql](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/schemas/matchmaking_service.sql)**
> 9.  🤝 **[meeting_service.sql](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/schemas/meeting_service.sql)**
> 10. 🔔 **[notification_service.sql](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/schemas/notification_service.sql)**
>
> Ngoài ra, bạn vẫn có thể dùng file tổng hợp **[setup_mysql.sql](file:///C:/Users/Windows%2010/.gemini/antigravity/brain/13100573-443e-434d-8fcb-2a262043bdaa/setup_mysql.sql)** nếu muốn import tất cả vào một database duy nhất.
