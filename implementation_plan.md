# Implementation Plan - Enhanced Admin BFF Features

Mục tiêu là mở rộng khả năng quản trị của `admin-bff`, cho phép Admin thực hiện các tác vụ quan trọng như duyệt Startup, quản lý người dùng và theo dõi chỉ số toàn hệ thống một cách tập trung.

## Proposed Changes

### [Component] Admin BFF (BFF Layer)

#### [MODIFY] [views.py](file:///d:/Django_project/api-gateway_vs_bff/bff/admin-bff/api/views.py)
- Sửa lỗi trong hàm `dashboard`: Định nghĩa chính xác các biến stats và tổng hợp dữ liệu từ User, Startup, và Booking services.
- Thêm hàm `approve_startup(request, startup_id)`: Gọi endpoint `approve` của Startup Service.
- Thêm hàm `reject_startup(request, startup_id)`: Gọi endpoint `reject` của Startup Service.
- Thêm hàm `block_user(request, user_id)`: Cập nhật trạng thái `banned=True` qua User Service.
- Thêm hàm `unblock_user(request, user_id)`: Cập nhật trạng thái `banned=False` qua User Service.
- Xóa các hàm liên quan đến `inventory` (đã cũ).

#### [MODIFY] [urls.py](file:///d:/Django_project/api-gateway_vs_bff/bff/admin-bff/api/urls.py)
- Cập nhật các route mới:
    - `/startups/<id>/approve/`
    - `/startups/<id>/reject/`
    - `/users/<id>/block/`
    - `/users/<id>/unblock/`
- Xóa các route liên quan đến `inventory`.

### [Component] Admin Frontend (Frontend Layer)

#### [MODIFY] [admin.html](file:///d:/Django_project/api-gateway_vs_bff/frontend/admin/admin.html)
- **Sidebar**: Loại bỏ mục "Kho cổ phần", thêm mục "Tổng quan" (Dashboard Stats).
- **Dashboard Section**: Thêm một section mới hiển thị các chỉ số tổng hợp (Người dùng, Startup, Hệ thống).
- **Startup Section**: Cập nhật bảng để hiển thị trạng thái (APPROVED/PENDING) và thêm nút "Duyệt"/"Từ chối" cho các startup đang chờ.
- **User Section**: Cập nhật hàm xử lý khóa người dùng để gọi đúng các endpoint `block`/`unblock` mới.
- **Cleanup**: Xóa bỏ toàn bộ HTML/JS liên quan đến `inventory`.

### [Component] Authorization & Security (BFF Layer)

#### [MODIFY] [views.py](file:///d:/Django_project/api-gateway_vs_bff/bff/admin-bff/api/views.py)
- **Decorator `admin_required`**: Thêm một decorator mới để kiểm tra header `X-Role`. Nếu `X-Role != 'admin'`, trả về `403 Forbidden`.
- **Áp dụng Decorator**: Thêm `@admin_required` vào các function:
    - `dashboard`
    - `startups` (cho hành động POST)
    - `startup_detail` (PUT, DELETE)
    - `pitch_slots`
    - `pitch_slot_status`
    - `users`
    - `user_detail`
    - `approve_startup`
    - `reject_startup`
    - `block_user`
    - `unblock_user`

## Verification Plan

### Automated Tests
- Sử dụng `curl` hoặc Postman để kiểm tra các hành động Admin mới qua API Gateway (cổng 80 - route `/admin/*`).
- Kiểm tra dashboard stats qua `http://localhost/admin/dashboard/`.

### Manual Verification
- Truy cập Admin Dashboard thông qua APISIX và xác nhận các chỉ số hiển thị chính xác.
- Thử approve/reject một startup mẫu và kiểm tra trạng thái trong database.
