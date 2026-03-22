# 📅 Scheduling Service - Documentation

## 1. Vai trò (Purpose)
Quản lý thời gian rảnh (Availability) của Nhà đầu tư và các khung giờ (Slots) để Startup có thể đặt lịch Pitching.

## 2. Các luồng dữ liệu (Data Flows)

### A. Luồng Quản lý Availability
- **Input:** Investor thiết lập lịch rảnh định kỳ (VD: Thứ 2 hàng tuần).
- **Logic:** Tự động tạo ra các `pitch_slots` tương ứng trong tương lai.

### B. Luồng Cập nhật Slot
- **Input:** Tin nhắn từ `booking-service` báo có người đặt hoặc hủy.
- **Logic:** Đổi trạng thái `pitch_slots` (AVAILABLE -> BOOKED/BLOCKED).

## 3. Sự kiện Kafka (Kafka Events)
- **Consumer:** Nghe `pitch_booking_cancelled` để mở lại (re-open) các slot đã bị hủy.
- **Producer:** `pitching_events`
    - `slot_updated`: Thông báo thay đổi khung giờ.

## 4. Cấu trúc Database (Models)

### Bảng `availability_templates`
Mẫu thời gian rảnh định kỳ của Investor.
- `day_of_week`: Thứ trong tuần (0-6).
- `start_time` / `end_time`: Khung giờ rảnh.

### Bảng `pitch_slots`
Các khung giờ cụ thể được tạo ra từ mẫu để Startup đặt chỗ.
- `status`: Trạng thái (`AVAILABLE`, `BOOKED`, `BLOCKED`).
