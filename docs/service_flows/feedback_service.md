# 💬 Feedback Service - Documentation

## 1. Vai trò (Purpose)
Thu thập ý kiến phản hồi từ Nhà đầu tư sau buổi Pitch và theo dõi mức độ quan tâm đầu tư thực tế.

## 2. Các luồng dữ liệu (Data Flows)

### A. Luồng Đánh giá sau Pitch
- **Investor** nhập đánh giá -> Lưu vào bảng `feedbacks`.

### B. Luồng Theo dõi quan tâm (Investment Interest)
- **Input:** Investor đánh giá "INTERESTED".
- **Logic:** Lưu vào bảng `investment_interests`.
- **Output:** Bắn sự kiện `investment_interest_tracked` qua Kafka.

## 3. Sự kiện Kafka (Kafka Events)
- **Producer:** `feedback_events`
    - `investment_interest_tracked`: Dùng để báo cho Startup và gửi dữ liệu cho dịch vụ Gợi ý (Matchmaking).

## 4. Cấu trúc Database (Models)

### Bảng `feedbacks`
Đánh giá nội bộ của Investor sau khi nghe Pitch.
- `rating`: Điểm đánh giá (1-5).
- `comment`: Nhận xét chuyên môn.

### Bảng `investment_interests`
Ghi nhận mong muốn đầu tư thực tế.
- `status`: Mức độ quan tâm (`INTERESTED`, `FOLLOW_UP`).
- `note`: Ghi chú thêm.
