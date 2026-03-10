# 🔐 Thông tin API Đăng nhập

## API Endpoint

```
POST http://localhost:8000/web/users/login/
```

## Request Body (JSON)

```json
{
  "username": "john_doe",
  "password": "password123"
}
```

## Response Success (200)

```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "",
    "is_staff": false,
    "banned": false,
    "created_at": "2026-03-08T17:28:21.105162Z"
  }
}
```

## Response Error (401)

```json
{
  "error": "Invalid credentials"
}
```

---

## 📋 Danh sách tài khoản TEST có sẵn

### ✅ Tài khoản hoạt động:

| Username      | Password      | Email              | Trạng thái |
|--------------|---------------|-------------------|------------|
| **john_doe**     | password123   | john@example.com  | ✅ Active  |
| **jane_smith**   | password123   | jane@example.com  | ✅ Active  |
| **admin_user**   | ❓ (chưa biết)  | admin@example.com | ⚠️ Unknown |
| **librarian**    | ❓ (tự đặt)    | ando21445@gmail.com | ⚠️ Unknown |
| **librarian1**   | ❓ (tự đặt)    | and21445@gmail.com  | ⚠️ Unknown |

---

## 🧪 Cách test API

### 1. Dùng cURL (cmd/bash):
```bash
curl -X POST http://localhost:8000/web/users/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"john_doe\",\"password\":\"password123\"}"
```

### 2. Dùng PowerShell:
```powershell
$body = '{"username":"john_doe","password":"password123"}'
Invoke-WebRequest -Uri "http://localhost:8000/web/users/login/" `
  -Method POST `
  -Body $body `
  -ContentType "application/json" `
  -UseBasicParsing
```

### 3. Dùng Frontend:
Truy cập: **http://localhost:8080/login_new.html**

---

## 🔑 Lưu ý:

1. **Token JWT** trả về có thời hạn (thường 5 phút cho access token)
2. Sử dụng **refresh token** để lấy access token mới
3. Thêm token vào header khi gọi API cần authentication:
   ```
   Authorization: Bearer <your_token>
   ```

## 🔧 Các API liên quan:

- **Đăng ký:** `POST /web/users/register/`
- **Lấy danh sách sản phẩm:** `GET /web/products/`
- **Tạo đơn hàng:** `POST /web/orders/create/` (cần token)
- **Xem đơn hàng:** `GET /web/orders/` (cần token)
