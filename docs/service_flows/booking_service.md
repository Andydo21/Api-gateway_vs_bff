# 📝 Booking Service - Documentation

## 1. Vai trò (Purpose)
Xử lý quy trình đăng ký Pitching và đặt chỗ (Booking). Đây là "trái tim" của quy trình nghiệp vụ.

## 2. Các luồng dữ liệu (Data Flows)

### A. Luồng Đăng ký (Pitch Request)
- **Startup** gửi yêu cầu -> Trạng thái ban đầu: `REGISTERED`.

### B. Luồng Phê duyệt (Approval Flow) - **NEW**
- **Admin/Investor** duyệt -> Trạng thái: `APPROVED`.
- Bắn sự kiện `pitch_request_approved` qua Kafka.

### C. Luồng Đặt chỗ (Booking Flow)
- Khi Startup chọn Slot -> Tạo `PitchBooking`.
- Bắn sự kiện `pitch_booking_created` qua Kafka.

## 3. Sự kiện Kafka (Kafka Events)
- **Producer:** `pitching_events`
    - `pitch_booking_created`: Sự kiện quan trọng nhất để kích hoạt tạo Meeting và gửi Thông báo.
    - `pitch_booking_cancelled`: Để giải phóng Slot.

## 4. Cấu trúc Database (Models)

### Bảng `pitch_requests`
Đơn đăng ký pitching của Startup.
- `pitch_deck_url`: Link tới file thuyết trình.
- `status`: Trạng thái (`REGISTERED`, `APPROVED`, `REJECTED`).

### Bảng `pitch_bookings`
Lịch pitching đã được xác nhận.
- `pitch_slot_id`: ID của khung giờ từ Scheduling service.

### Bảng `waitlists`
Danh sách các Startup đang chờ nếu khung giờ đó đã có người đặt trước.
