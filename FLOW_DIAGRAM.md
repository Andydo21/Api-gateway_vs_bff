# 🔄 LUỒNG CHẠY CHI TIẾT - API GATEWAY + BFF + MICROSERVICES

## 📊 KIẾN TRÚC TỔNG QUÁT

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER / CLIENT                          │
│                      (index.html, JS)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP Requests (Multiple APIs)
                         │ 1. GET /web/categories/
                         │ 2. GET /web/products/
                         │ 3. GET /web/products/{id}/reviews/
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
│              🎯 WEB-BFF (Port 8001)                             │
│  - Aggregate data từ nhiều microservices                        │
│  - Optimize response cho Web client                             │
│  - Cache responses                                              │
│                                                                  │
│  Routes:                                                         │
│  ├─ GET /categories/     → category_list()                      │
│  ├─ GET /products/       → product_list()                       │
│  └─ GET /products/{id}/reviews/ → product_reviews()             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Multiple parallel calls
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Product    │  │   Product    │  │   Product    │
│   Service    │  │   Service    │  │   Service    │
│  (Port 4002) │  │  (Port 4002) │  │  (Port 4002) │
│              │  │              │  │              │
│ /categories/ │  │  /products/  │  │/products/{id}│
│              │  │              │  │  /reviews/   │
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
    loadProducts();     // Load data
    updateCartCount();  // Update giỏ hàng
};
```

---

### **BƯỚC 2: Frontend Gọi 3 API Song Song**
**File:** `frontend/web/index.html` - function `loadProducts()`

```javascript
console.log('🚀 [FRONTEND] Bắt đầu load data từ API Gateway...');

// 1️⃣ GỌI API CATEGORIES
console.log('📂 [FRONTEND → GATEWAY] GET /web/categories/');
const categoriesPromise = fetch(`${API_BASE}/web/categories/`);

// 2️⃣ GỌI API PRODUCTS
console.log('📦 [FRONTEND → GATEWAY] GET /web/products/');
const productsPromise = fetch(`${API_BASE}/web/products/`);

// 3️⃣ GỌI SONG SONG - Tối ưu performance
const [categoriesData, productsData] = await Promise.all([
    categoriesPromise,
    productsPromise
]);

// 4️⃣ GỌI API REVIEWS cho 3 sản phẩm đầu
await loadProductReviews(allProducts.slice(0, 3));
```

**Giải thích:**
- ✅ Frontend **gọi riêng biệt** 3 endpoints khác nhau
- ✅ Tất cả requests đều qua **API Gateway**
- ✅ Thể hiện rõ **pattern phân tách** services

---

### **BƯỚC 3: API Gateway Xử Lý (Port 8080)**

#### **3.1 JWT Authentication Middleware**
**File:** `api-gateway/gateway/auth_middleware.py`

```python
class JWTAuthenticationMiddleware:
    def __call__(self, request):
        # Skip public paths
        if self.is_public_path(request.path):
            return self.get_response(request)
        
        # Get Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = auth_header.replace('Bearer ', '')
        
        # Decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY)
        
        # 🔑 INJECT USER INFO vào headers
        request.META['HTTP_X_USER_ID'] = str(payload['user_id'])
        request.META['HTTP_X_USERNAME'] = payload['username']
        request.META['HTTP_X_EMAIL'] = payload.get('email', '')
        
        # Forward to BFF
        return self.get_response(request)
```

**Console Output:**
```
🔍 [AUTH] Path: /web/categories/
🔍 [AUTH] Authorization header: Bearer eyJhbGc...
✅ [AUTH] Token valid, User ID: 123
```

#### **3.2 Proxy to BFF**
**File:** `api-gateway/gateway/views.py` - class `WebBFFProxy`

```python
class WebBFFProxy(ProxyView):
    target_url = 'http://web-bff:8001'
    
    def dispatch(self, request, *args, **kwargs):
        path = kwargs.get('path', '')
        url = f"{self.target_url}/{path}"
        
        # Forward với headers (JWT + User info)
        headers = self.get_headers(request)  # Bao gồm X-User-ID
        response = requests.get(url, headers=headers)
        
        return HttpResponse(response.content)
```

**Request được forward:**
```
GET http://web-bff:8001/categories/
Headers:
  - Authorization: Bearer eyJhbGc...
  - X-User-ID: 123
  - X-Username: john_doe
```

---

### **BƯỚC 4: Web-BFF Xử Lý (Port 8001)**

#### **4.1 Request 1: GET /categories/**
**File:** `bff/web-bff/api/views.py` - function `category_list()`

```python
@api_view(['GET'])
@cache_page(60 * 15)  # Cache 15 phút
def category_list(request):
    print('📂 [BFF] Nhận request GET /categories/ từ Gateway')
    print('📂 [BFF → PRODUCT-SERVICE] Forward request đến Product Service')
    
    # Forward to Product Service
    response = requests.get(f'{PRODUCT_SERVICE}/categories/', timeout=5)
    # PRODUCT_SERVICE = 'http://product-service:4002'
    
    categories = response.json()
    print(f'✅ [BFF] Nhận {len(categories)} categories từ Product Service')
    
    return Response({
        'success': True,
        'categories': categories,
        'source': 'web-bff',
        'upstream': 'product-service'
    })
```

**Console Output:**
```
📂 [BFF] Nhận request GET /categories/ từ Gateway
📂 [BFF → PRODUCT-SERVICE] Forward request đến Product Service
✅ [BFF] Nhận 5 categories từ Product Service
```

#### **4.2 Request 2: GET /products/**
**File:** `bff/web-bff/api/views.py` - function `product_list()`

```python
@api_view(['GET'])
@cache_page(60 * 5)  # Cache 5 phút
def product_list(request):
    print('📦 [BFF] Nhận request GET /products/ từ Gateway')
    
    # 1️⃣ Get products from Product Service
    products_response = requests.get(f'{PRODUCT_SERVICE}/products/', timeout=5)
    products = products_response.json()
    print(f'✅ [BFF] Nhận {len(products)} products từ Product Service')
    
    # 2️⃣ Get categories (parallel)
    categories_response = requests.get(f'{PRODUCT_SERVICE}/categories/', timeout=3)
    categories = categories_response.json()
    
    # 3️⃣ Enrich products với review data
    for idx, product in enumerate(products[:10]):
        reviews_response = requests.get(
            f'{PRODUCT_SERVICE}/products/{product["id"]}/reviews/summary/'
        )
        if reviews_response.status_code == 200:
            review_data = reviews_response.json()
            product['rating'] = review_data.get('average_rating', 4.5)
            product['review_count'] = review_data.get('count', 0)
    
    # 🎯 AGGREGATION: Return combined data
    return Response({
        'success': True,
        'products': products,
        'categories': categories,
        'bff_info': {
            'aggregated_from': ['product-service'],
            'services_called': 2 + len(products[:10]),
            'source': 'web-bff'
        }
    })
```

**Console Output:**
```
📦 [BFF] Nhận request GET /products/ từ Gateway
📦 [BFF → PRODUCT-SERVICE] GET /products/
✅ [BFF] Nhận 24 products từ Product Service
📦 [BFF → PRODUCT-SERVICE] GET /categories/
✅ [BFF] Nhận 5 categories từ Product Service
⭐ [BFF → PRODUCT-SERVICE] GET /products/1/reviews/summary/
⭐ [BFF → PRODUCT-SERVICE] GET /products/2/reviews/summary/
⭐ [BFF → PRODUCT-SERVICE] GET /products/3/reviews/summary/
✅ [BFF] Aggregated data từ 13 API calls
```

**✨ KEY POINT - BFF PATTERN:**
- BFF gọi **NHIỀU microservices** (Products + Categories + Reviews)
- **Aggregate data** thành 1 response duy nhất
- Frontend chỉ cần 1 API call nhận đủ data
- **Performance tối ưu** - giảm round-trips

#### **4.3 Request 3: GET /products/{id}/reviews/**
**File:** `bff/web-bff/api/views.py` - function `product_reviews()`

```python
@api_view(['GET'])
@cache_page(60 * 5)
def product_reviews(request, product_id):
    print(f'⭐ [BFF] Nhận request GET /products/{product_id}/reviews/')
    print(f'⭐ [BFF → PRODUCT-SERVICE] Forward request đến Product Service')
    
    # Get reviews list
    reviews_response = requests.get(
        f'{PRODUCT_SERVICE}/products/{product_id}/reviews/'
    )
    
    # Get reviews summary
    summary_response = requests.get(
        f'{PRODUCT_SERVICE}/products/{product_id}/reviews/summary/'
    )
    
    reviews = reviews_response.json() if reviews_response.status_code == 200 else []
    summary = summary_response.json() if summary_response.status_code == 200 else {}
    
    return Response({
        'success': True,
        'reviews': reviews,
        'average_rating': summary.get('average_rating', 0),
        'count': summary.get('count', 0),
        'source': 'web-bff',
        'upstream': 'product-service'
    })
```

---

### **BƯỚC 5: Product Microservice Xử Lý (Port 4002)**

#### **5.1 Categories Endpoint**
**File:** `microservices/product-service/api/urls.py`
```python
router.register(r'categories', views.CategoryViewSet)
```

**File:** `microservices/product-service/api/views.py`
```python
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
```

**File:** `microservices/product-service/api/serializers.py`
```python
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']
```

**Database Query:**
```sql
SELECT id, name, description, created_at 
FROM api_category 
ORDER BY id;
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic devices",
    "created_at": "2024-01-15T10:30:00Z"
  },
  ...
]
```

#### **5.2 Products Endpoint**
**File:** `microservices/product-service/api/views.py`
```python
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Filters
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        featured = self.request.query_params.get('featured')
        
        if category:
            queryset = queryset.filter(category_id=category)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        if featured == 'true':
            queryset = queryset.filter(featured=True)
        
        return queryset
```

**File:** `microservices/product-service/api/serializers.py`
```python
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 
                  'category_name', 'stock', 'image_url', 'thumbnail', 
                  'featured', 'rating', 'created_at', 'updated_at']
```

**Database Query:**
```sql
SELECT p.id, p.name, p.description, p.price, p.stock, p.image_url,
       c.name as category_name
FROM api_product p
LEFT JOIN api_category c ON p.category_id = c.id
WHERE p.featured = true
ORDER BY p.created_at DESC;
```

#### **5.3 Reviews Endpoint**
**File:** `microservices/product-service/api/views.py`
```python
class ProductViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get product reviews"""
        product = self.get_object()
        reviews = product.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='reviews/summary')
    def reviews_summary(self, request, pk=None):
        """Get reviews summary"""
        product = self.get_object()
        reviews = product.reviews.all()
        
        avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg']
        
        return Response({
            'product_id': product.id,
            'average_rating': round(avg_rating, 1) if avg_rating else 0,
            'count': reviews.count(),
            'ratings_distribution': {
                '5': reviews.filter(rating=5).count(),
                '4': reviews.filter(rating=4).count(),
                '3': reviews.filter(rating=3).count(),
                '2': reviews.filter(rating=2).count(),
                '1': reviews.filter(rating=1).count(),
            }
        })
```

**Database Query:**
```sql
-- Get reviews
SELECT id, product_id, user_id, username, rating, comment, created_at
FROM api_review
WHERE product_id = 1
ORDER BY created_at DESC;

-- Get rating summary
SELECT 
    AVG(rating) as avg_rating,
    COUNT(*) as total_count,
    SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as five_stars,
    SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as four_stars,
    SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as three_stars,
    SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as two_stars,
    SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as one_star
FROM api_review
WHERE product_id = 1;
```

---

### **BƯỚC 6: Response Trả Về**

```
PostgreSQL DB
    ↓ (SQL Query Results)
Product Service
    ↓ (JSON Response)
Web-BFF (Aggregate & Format)
    ↓ (Combined JSON)
API Gateway (Forward)
    ↓ (HTTP Response)
Browser (Render UI)
```

**Final Response to Frontend:**
```json
{
  "success": true,
  "categories": [...],
  "products": [...],
  "reviews": [...],
  "source": "web-bff",
  "upstream": "product-service"
}
```

---

## 🎯 SO SÁNH: TRƯỚC vs SAU

### **❌ TRƯỚC (Không rõ pattern):**
```javascript
// Frontend chỉ gọi 1 API
fetch('/web/products/')

// BFF aggregate ngầm phía sau
// Frontend KHÔNG BIẾT có bao nhiêu services được gọi
```

### **✅ SAU (Thể hiện rõ pattern):**
```javascript
// Frontend gọi RIÊNG BIỆT 3 APIs
fetch('/web/categories/')    // → Gateway → BFF → Product Service
fetch('/web/products/')       // → Gateway → BFF → Product Service  
fetch('/web/products/1/reviews/') // → Gateway → BFF → Product Service

// Console logs thể hiện rõ luồng:
// 📂 [FRONTEND → GATEWAY] GET /web/categories/
// 📂 [BFF → PRODUCT-SERVICE] Forward request
// ✅ [BFF] Nhận 5 categories
```

---

## 📊 TỔNG KẾT PATTERNS

### **1. API Gateway Pattern**
- ✅ **Single entry point** - Tất cả requests qua 1 cổng
- ✅ **Authentication** - JWT validation tập trung
- ✅ **User context injection** - Inject X-User-ID headers
- ✅ **Routing** - Forward đến đúng BFF service

### **2. BFF Pattern (Backend for Frontend)**
- ✅ **Data Aggregation** - Gọi nhiều microservices, trả về 1 response
- ✅ **Client-optimized APIs** - Web-BFF khác Admin-BFF
- ✅ **Caching** - Cache ở BFF layer
- ✅ **Response transformation** - Format data theo nhu cầu frontend

### **3. Microservices Pattern**
- ✅ **Single Responsibility** - Mỗi service 1 domain (Product/Order/User)
- ✅ **Independent** - Deploy riêng, scale riêng
- ✅ **RESTful APIs** - Chuẩn REST conventions
- ✅ **Database per service** - Mỗi service có DB riêng

---

## 🔍 CÁCH TEST LUỒNG

### **1. Mở Browser Console**
```
F12 → Console tab
```

### **2. Load trang index.html**
```
http://localhost:8080/ui/web/index.html
```

### **3. Xem logs**
```
🚀 [FRONTEND] Bắt đầu load data từ API Gateway...
📂 [FRONTEND → GATEWAY] GET /web/categories/
📦 [FRONTEND → GATEWAY] GET /web/products/
⚡ [FRONTEND] Gọi song song 2 API...
✅ [FRONTEND] Nhận response từ Categories
✅ [FRONTEND] Nhận response từ Products
⭐ [FRONTEND → GATEWAY] GET /web/products/1/reviews/
✅ [FRONTEND] Product 1 có 5 reviews
🎉 [FRONTEND] Hoàn tất load trang chủ!
```

### **4. Xem Docker logs**
```bash
# BFF logs
docker logs web-bff

# Product Service logs  
docker logs product-service
```

---

## 🚀 NEXT STEPS

Để thể hiện **HOÀN TOÀN** pattern, có thể thêm:

1. **Distributed Tracing** - OpenTelemetry/Jaeger để trace requests
2. **Request ID** - Generate unique ID cho mỗi request, log throughout
3. **Metrics** - Prometheus metrics cho mỗi service
4. **Circuit Breaker** - Resilience khi service down
5. **API Versioning** - /v1/products, /v2/products

**Tài liệu tham khảo:**
- [README.md](README.md) - Setup guide
- [API_LOGIN_INFO.md](API_LOGIN_INFO.md) - Authentication details
- [LOGGING_AND_CACHING.md](LOGGING_AND_CACHING.md) - Logging strategy
