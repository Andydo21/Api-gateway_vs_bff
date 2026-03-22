# 💰 Funding Service - Documentation

## 1. Vai trò (Purpose)
Quản lý các giao dịch tài chính, thanh toán phí tham gia sự kiện hoặc phí dịch vụ.

## 2. Các luồng dữ liệu (Data Flows)

### A. Luồng Thanh toán (Payment Flow)
- **Input:** Request từ Web-BFF khi user chọn cổng thanh toán.
- **Logic:** Kết nối với Gateway thanh toán, lưu trạng thái `payments`.
- **Output:** Bắn sự kiện `payment_completed` hoặc `payment_failed`.

## 3. Sự kiện Kafka (Kafka Events)
- **Producer:** `finance_events`
    - `payment_completed`: Kích hoạt việc cập nhật trạng thái đơn hàng/booking ở các dịch vụ khác.

## 4. Cấu trúc Database (Models)

### Bảng `payments`
Ghi nhận các giao dịch thanh toán.
- `amount`: Số tiền.
- `payment_method`: Phương thức (`Stripe`, `Paypal`, `Momo`).
- `status`: Trạng thái (`pending`, `completed`, `failed`).
- `transaction_id`: Mã giao dịch từ cổng thanh toán.
