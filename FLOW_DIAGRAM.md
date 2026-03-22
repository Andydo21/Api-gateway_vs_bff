# 🔄 LUỒNG CHẠY CHI TIẾT - API GATEWAY + BFF + MICROSERVICES

## 📊 KIẾN TRÚC TỔNG QUÁT

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER / CLIENT                          │
│                    (index.html, pitch-requests.html)             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP Requests (Multiple APIs)
                         │ 1. GET /web/categories/
                         │ 2. GET /web/startups/
                         │ 3. GET /web/pitch-requests/
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              🚪 API GATEWAY (Port 8080)                         │
│  - JWT Authentication (auth_middleware.py)                      │
│  - Validate token & Extract user info                           │
│  - Inject headers: X-User-ID, X-Username                        │
│  - Route to BFF services                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Forward với user headers
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              🎯 WEB-BFF (Port 3001)                             │
│  - Aggregate data từ nhiều microservices                        │
│  - Optimize response cho Web client                             │
│  - Cache responses                                              │
│                                                                  │
│  Routes:                                                         │
│  ├─ GET /categories/     → category_list()                      │
│  ├─ GET /startups/       → startup_list()                       │
│  └─ GET /pitch-requests/ → pitch_request_get()                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Multiple parallel calls
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Startup    │  │Pitch Request │  │     User     │
│   Service    │  │   Service    │  │   Service    │
│  (Port 4002) │  │  (Port 4003) │  │  (Port 4001) │
│              │  │              │  │              │
│ /categories/ │  │ /pitch-reqs/ │  │    /users/   │
│              │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┴────────────────┘
                         │
                         ▼
                   PostgreSQL DB
```

---

## 🎯 LUỒNG CHI TIẾT - TRANG CHỦ (index.html)

### **BƯỚC 1: Browser Load Trang**
**File:** `frontend/web/index.html`

```javascript
// Khi trang load
window.onload = () => {
    checkAuth();        // Kiểm tra login
    loadStartups();     // Load danh sách Startup
    updatePitchCount(); // Cập nhật số lượng Pitch quan tâm
};
```

---

### **BƯỚC 2: Frontend Gọi API Qua Gateway**
**File:** `frontend/web/index.html` - function `loadStartups()`

```javascript
console.log('🚀 [FRONTEND] Bắt đầu load data từ API Gateway...');

// 1️⃣ GỌI API CATEGORIES
console.log('📂 [FRONTEND → GATEWAY] GET /web/categories/');
const categoriesPromise = fetch(`${API_BASE}/web/categories/`);

// 2️⃣ GỌI API STARTUPS
console.log('📦 [FRONTEND → GATEWAY] GET /web/startups/');
const startupsPromise = fetch(`${API_BASE}/web/startups/`);

// 3️⃣ GỌI SONG SONG - Tối ưu performance
const [categoriesData, startupsData] = await Promise.all([
    categoriesPromise,
    startupsPromise
]);
```

---

### **BƯỚC 3: API Gateway Xử Lý (Port 8080)**

#### **3.1 JWT Authentication Middleware**
**File:** `api-gateway/gateway/auth_middleware.py`

```python
class JWTAuthenticationMiddleware:
    def __call__(self, request):
        # Validate token & Inject USER INFO vào headers
        request.META['HTTP_X_USER_ID'] = str(payload['user_id'])
        request.META['HTTP_X_USERNAME'] = payload['username']
        
        # Forward to BFF
        return self.get_response(request)
```

#### **3.2 Proxy to BFF**
**File:** `api-gateway/gateway/views.py`

```python
class WebBFFProxy(ProxyView):
    target_url = 'http://web-bff:3001'
    # Forward request đến Web-BFF với đầy đủ User Headers
```

---

### **BƯỚC 4: Web-BFF Xử Lý (Port 3001)**

#### **4.1 Gửi Yêu Cầu Pitch (Pitch Request)**
**File:** `bff/web-bff/api/views.py` - function `pitch_request_add()`

```python
@api_view(['POST'])
def pitch_request_add(request):
    print('💼 [BFF] Nhận yêu cầu thêm Pitch quan tâm')
    
    # Forward đến Order Service (nay là Pitch/Order Service)
    response = requests.post(f'{ORDER_SERVICE}/pitch-requests/add/', json=data)
    
    return Response(response.json())
```

---

### **BƯỚC 5: Pitch Request / Order Service Xử Lý (Port 4003)**

**File:** `microservices/order-service/api/models.py`
```python
class PitchRequest(models.Model):
    user_id = models.IntegerField(unique=True)
    # ...
    
class PitchItem(models.Model):
    pitch_request = models.ForeignKey(PitchRequest, related_name='items', ...)
    startup_id = models.IntegerField()
    quantity = models.IntegerField(default=1)
```

---

## 📊 TỔNG KẾT PATTERNS

### **1. API Gateway Pattern**
- ✅ **Single entry point** cho toàn bộ hệ thống.
- ✅ **Authentication** tập trung tại Gateway.
- ✅ **User context injection** qua HTTP Headers.

### **2. BFF Pattern (Backend for Frontend)**
- ✅ **Data Aggregation**: Kết hợp dữ liệu từ nhiều service (Startup, User, Pitch).
- ✅ **Simplified API**: Cung cấp API tinh gọn cho Frontend Web.

### **3. Microservices Pattern**
- ✅ **Domain-driven**: Mỗi service quản lý một nghiệp vụ riêng (Startup, Order/Pitch, Inventory).
- ✅ **Database per Service**: Mỗi service có schema riêng, không truy cập chéo DB.
