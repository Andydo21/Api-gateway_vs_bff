# Jira & GitHub Professional Workflow Guide

Cuốn hướng dẫn này giúp bạn tối ưu hóa sự kết nối giữa việc lập trình trên GitHub và quản lý công việc trên Jira cho dự án **SCRUM**.

---

## 🚀 1. Smart Commits (Commit Thông Minh)

Jira có tính năng tự động đọc commit của bạn để cập nhật trạng thái thẻ. Cú pháp cơ bản:
`MÃ-THẺ #LỆNH [bình luận]`

### Các lệnh phổ biến:
- **Chuyển trạng thái**: `#done`, `#in-progress`, `#to-do`
  - *Ví dụ:* `SCRUM-1 #done Hoàn thành tích hợp gateway`
- **Thêm bình luận**: `#comment`
  - *Ví dụ:* `SCRUM-2 #comment Đã fix lỗi kết nối Kafka`
- **Ghi log thời gian**: `#time`
  - *Ví dụ:* `SCRUM-1 #time 1h 30m Working on views`

> [!TIP]
> Bạn có thể kết hợp nhiều lệnh: `SCRUM-1 #done #time 2h Task completed!`

---

## 🌿 2. Quy trình làm việc với Nhánh (Branch)

Để Jira tự động nhóm các commit và hiển thị trong bảng "Development":

1.  **Đặt tên nhánh**: Luôn bắt đầu bằng mã thẻ Jira.
    - `SCRUM-1-feature-auth`
    - `SCRUM-2-bugfix-api`
2.  **Tạo Pull Request (PR)**: Khi bạn tạo PR trên GitHub, Jira sẽ hiển thị trạng thái PR ngay trong thẻ. Nếu bạn gộp (Merge) PR, Jira có thể tự động đóng task (tùy vào Automation Rule bạn đã cài).

---

## 🛠 3. Công cụ hỗ trợ: `git-sync.ps1`

Để giúp bạn không quên mã thẻ Jira khi commit, chúng tôi cung cấp script `scripts/git-sync.ps1`.

### Cách sử dụng:
1. Mở PowerShell trong thư mục dự án.
2. Chạy lệnh: `./scripts/git-sync.ps1`
3. Nhập mã thẻ Jira (ví dụ: `SCRUM-1`) và thông điệp commit.
4. Script sẽ tự động commit và đẩy (push) code cho bạn.

---

## 📈 4. Quản lý Hierarchy (Cấp bậc)

Theo Automation Rule bạn đã cài:
- Khi một **Task Cha** được chuyển sang **Done**, toàn bộ **Task Con** sẽ tự động được đóng lại.
- Hãy đảm bảo bạn đã liên kết (Link) các task con vào task cha một cách chính xác trước khi thực hiện.

---

*Tài liệu này được tạo bởi Antigravity để hỗ trợ quy trình Scrum cho team.*
