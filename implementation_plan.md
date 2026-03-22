# Implementation Plan - Saga Pattern (Pitch Booking)

Mục tiêu là triển khai Saga Pattern (Choreography) để đảm bảo tính nhất quán dữ liệu khi thực hiện quy trình Đặt lịch Pitch (Booking -> Scheduling -> Meeting).

## Proposed Changes

### 1. [booking-service](file:///d:/Django_project/api-gateway_vs_bff/microservices/booking-service/api/models.py)
- Cập nhật trạng thái `PitchBooking`: `INITIALIZED`, `CONFIRMED`, `FAILED`.

### 2. [booking-service Views](file:///d:/Django_project/api-gateway_vs_bff/microservices/booking-service/api/views.py)
- API `create` sẽ tạo booking với trạng thái `INITIALIZED` và bắn sự kiện `booking_initiated`.

### 3. [scheduling-service](file:///d:/Django_project/api-gateway_vs_bff/microservices/scheduling-service/api/management/commands/run_kafka_consumer.py) [NEW]
- Lắng nghe `booking_initiated`.
- Thực hiện giữ chỗ (Slot -> `BOOKED`).
- Thành công: Bắn `slot_confirmed`.
- Thất bại: Bắn `slot_failed`.

### 4. [meeting-service](file:///d:/Django_project/api-gateway_vs_bff/microservices/meeting-service/api/management/commands/run_kafka_consumer.py)
- Đổi từ lắng nghe `pitch_booking_created` sang `slot_confirmed`.
- Thành công: Bắn `meeting_created`.
- Thất bại: Bắn `meeting_failed`.

### 5. [booking-service Consumer](file:///d:/Django_project/api-gateway_vs_bff/microservices/booking-service/api/management/commands/run_kafka_consumer.py) [NEW]
- Lắng nghe `meeting_created` -> Chuyển status `CONFIRMED`.
- Lắng nghe `slot_failed` hoặc `meeting_failed` -> Chuyển status `FAILED` (Bù trừ).

### 6. Logic Bù trừ (Compensation)
- Nếu `Meeting Service` thất bại, `Scheduling Service` sẽ nghe `meeting_failed` để giải phóng Slot (Slot -> `AVAILABLE`).

## Verification Plan

### Automated Tests
- Gửi yêu cầu đặt lịch và kiểm tra chuỗi sự kiện trong Kafka.
- Giả lập lỗi ở Meeting Service để kiểm tra Slot có được giải phóng không.

### Manual Verification
- Kiểm tra trạng thái Booking trong Database của Booking Service sau khi toàn bộ quy trình hoàn tất.
