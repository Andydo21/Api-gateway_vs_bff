# Implementation Plan - True BFF Data Aggregation for Admin

Mục tiêu là biến `admin-bff` thành một lớp BFF thực thụ bằng cách thực hiện **Data Aggregation** (tổng hợp dữ liệu) từ nhiều microservices thay vì chỉ proxy yêu cầu.

## Proposed Changes

### [Component] Admin BFF (BFF Layer)

#### [MODIFY] [views.py](file:///d:/Django_project/api-gateway_vs_bff/bff/admin-bff/api/views.py)
- **Hàm `startups` (Aggregation)**: 
    - Lấy danh sách startup.
    - Duyệt qua từng startup, lấy thông tin `owner` (tên, email) từ User Service.
    - Tổng hợp thành một response duy nhất với đầy đủ thông tin founder.
- **Hàm `users` (Aggregation)**:
    - Lấy danh sách user.
    - Lấy số lượng startup mà mỗi user đang sở hữu từ Startup Service.
    - Trả về danh sách kèm theo business summary của từng người.
- **Hàm `user_detail` (Rich Profile)**:
    - Tổng hợp thông tin cơ bản, danh sách startup thuộc quyền sở hữu, và các lịch hẹn (pitch slots) gần đây của user đó.
- **Tối ưu hóa**: Sử dụng `threading` hoặc `asyncio` (nếu cần) để gọi các service song song nhằm giảm latency.

## Verification Plan

### Automated Tests
- Kiểm tra kết quả JSON của `/admin/startups/`: Đảm bảo có trường `owner_details` chứa thông tin từ User Service.
- Kiểm tra `/admin/users/`: Đảm bảo có trường `startup_count`.

### Manual Verification
- Kiểm tra Admin Dashboard UI: Xác nhận thông tin Founder hiển thị ngay trên bảng danh sách Startup mà không cần gọi API riêng.
