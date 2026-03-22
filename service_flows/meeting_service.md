# 🤝 Meeting Service - Documentation

## 1. Vai trò (Purpose)
Quản lý các phiên họp trực tuyến. Tự động hóa việc tạo link Zoom/Meet để người dùng không phải tạo thủ công.

## 2. Các luồng dữ liệu (Data Flows)

### A. Luồng Tự động tạo Meeting (Auto-Create)
- **Trigger:** Nhận sự kiện `pitch_booking_created` từ Kafka.
- **Logic:** Gọi API Zoom (giả lập) -> Tạo bản ghi `Meeting` -> Lưu `meeting_url`.
- **Output:** Bắn sự kiện `meeting_auto_created` để báo cho User.

## 3. Sự kiện Kafka (Kafka Events)
- **Consumer:** Nghe `pitching_events` (topic).
- **Producer:** `meeting_events`
    - `meeting_auto_created`: Gửi link phòng họp tới Notification Service để báo cho Startup và Investor.

## 4. Cấu trúc Database (Models)

### Bảng `meetings`
Quản lý các link họp trực tuyến.
- `booking_id`: Liên kết tới Booking tương ứng.
- `meeting_url`: Link Zoom/Google Meet.
- `meeting_type`: Loại phòng họp.
- `start_time` / `end_time`: Thời gian diễn ra.
- `status`: Trạng thái phòng họp (`ONGOING`, `ENDED`).
