# 🚀 Hướng dẫn cài đặt và chạy hệ thống

## Yêu cầu
- Docker Desktop
- Python 3.11+
- PostgreSQL 15 (hoặc sử dụng Docker)

## Bước 1: Chuẩn bị môi trường

### 1.1. Clone repository (nếu có)
```bash
cd d:\Django_project\api-gateway_vs_bff
```

### 1.2. Tạo file .env
Sao chép file `.env.example` thành `.env`:
```bash
copy .env.example .env
```

Cập nhật các giá trị trong `.env` nếu cần:
```env
# Database
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## Bước 2: Chạy với Docker Compose (Khuyến nghị)

### 2.1. Build và khởi động tất cả services
```bash
docker-compose up --build
```

Lệnh này sẽ khởi động:
- PostgreSQL (port 5432)
- API Gateway (port 8000)
- Web BFF (port 3001)
- Admin BFF (port 3002)
- User Service (port 4001)
- Product Service (port 4002)
- Order Service (port 4003)
- Payment Service (port 4004)
- Inventory Service (port 4005)
- Recommendation Service (port 4006)

### 2.2. Chạy migrations cho tất cả services

Mở terminal mới và chạy:

```bash
# User Service
docker-compose exec user-service python manage.py makemigrations
docker-compose exec user-service python manage.py migrate

# Product Service
docker-compose exec product-service python manage.py makemigrations
docker-compose exec product-service python manage.py migrate

# Order Service
docker-compose exec order-service python manage.py makemigrations
docker-compose exec order-service python manage.py migrate

# Payment Service
docker-compose exec payment-service python manage.py makemigrations
docker-compose exec payment-service python manage.py migrate

# Inventory Service
docker-compose exec inventory-service python manage.py makemigrations
docker-compose exec inventory-service python manage.py migrate

# Recommendation Service
docker-compose exec recommendation-service python manage.py makemigrations
docker-compose exec recommendation-service python manage.py migrate
```

### 2.3. Tạo superuser (Admin)
```bash
docker-compose exec user-service python manage.py createsuperuser
```

## Bước 3: Chạy thủ công (Không dùng Docker)

### 3.1. Cài đặt PostgreSQL
Tải và cài đặt PostgreSQL 15:
- https://www.postgresql.org/download/windows/

Tạo database:
```sql
CREATE DATABASE ecommerce_db;
```

### 3.2. Cài đặt dependencies cho từng service

#### API Gateway
```bash
cd api-gateway
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

#### Web BFF
```bash
cd bff/web-bff
pip install -r requirements.txt
python manage.py runserver 3001
```

#### Admin BFF
```bash
cd bff/admin-bff
pip install -r requirements.txt
python manage.py runserver 3002
```

#### User Service
```bash
cd microservices/user-service
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 4001
```

#### Product Service
```bash
cd microservices/product-service
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 4002
```

Tương tự cho các service còn lại (Order, Payment, Inventory, Recommendation).

## Bước 4: Tạo dữ liệu mẫu

### 4.1. Tạo sample data script
Tạo file `create_sample_data.py` trong thư mục root:

```python
import requests
import json

# API URLs
USER_SERVICE = "http://localhost:4001/api"
PRODUCT_SERVICE = "http://localhost:4002/api"
INVENTORY_SERVICE = "http://localhost:4005/api"

# 1. Create sample users
users_data = [
    {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe"
    },
    {
        "username": "jane_smith",
        "email": "jane@example.com",
        "password": "password123",
        "first_name": "Jane",
        "last_name": "Smith"
    }
]

print("Creating users...")
for user in users_data:
    response = requests.post(f"{USER_SERVICE}/register/", json=user)
    print(f"Created user: {user['username']}")

# 2. Create categories
categories = [
    {"name": "Electronics", "description": "Electronic devices"},
    {"name": "Clothing", "description": "Fashion and apparel"},
    {"name": "Books", "description": "Books and magazines"}
]

print("\nCreating categories...")
for cat in categories:
    response = requests.post(f"{PRODUCT_SERVICE}/categories/", json=cat)
    print(f"Created category: {cat['name']}")

# 3. Create products
products = [
    {
        "name": "iPhone 15 Pro",
        "description": "Latest Apple smartphone",
        "price": "29990000",
        "category": 1,
        "stock": 50,
        "featured": True
    },
    {
        "name": "Samsung Galaxy S24",
        "description": "Samsung flagship phone",
        "price": "25990000",
        "category": 1,
        "stock": 40,
        "featured": True
    },
    {
        "name": "MacBook Pro M3",
        "description": "Professional laptop",
        "price": "49990000",
        "category": 1,
        "stock": 20,
        "featured": True
    }
]

print("\nCreating products...")
created_products = []
for product in products:
    response = requests.post(f"{PRODUCT_SERVICE}/products/", json=product)
    if response.status_code == 201:
        data = response.json()
        created_products.append(data['data'])
        print(f"Created product: {product['name']}")

# 4. Create inventory for products
print("\nCreating inventory...")
for product in created_products:
    inventory_data = {
        "product_id": product['id'],
        "product_name": product['name'],
        "available_quantity": product['stock'],
        "reserved_quantity": 0,
        "reorder_level": 10
    }
    response = requests.post(f"{INVENTORY_SERVICE}/inventory/", json=inventory_data)
    print(f"Created inventory for: {product['name']}")

print("\n✅ Sample data created successfully!")
```

Chạy script:
```bash
python create_sample_data.py
```

## Bước 5: Truy cập ứng dụng

### Frontend
- **Website**: Mở file `frontend/web/index.html` trong trình duyệt
- **Admin Panel**: Mở file `frontend/admin/admin.html` trong trình duyệt

> **Lưu ý**: Để frontend hoạt động đúng, bạn cần chạy simple HTTP server:

```bash
# Trong thư mục frontend/web
python -m http.server 8080

# Truy cập: http://localhost:8080
```

```bash
# Trong thư mục frontend/admin
python -m http.server 8081

# Truy cập: http://localhost:8081/admin.html
```

### API Endpoints

#### API Gateway (Port 8000)
- Web BFF: `http://localhost:8000/web/`
- Admin BFF: `http://localhost:8000/admin-panel/`
- Health Check: `http://localhost:8000/health/`

#### Microservices (Direct Access)
- User Service: `http://localhost:4001/api/`
- Product Service: `http://localhost:4002/api/`
- Order Service: `http://localhost:4003/api/`
- Payment Service: `http://localhost:4004/api/`
- Inventory Service: `http://localhost:4005/api/`
- Recommendation Service: `http://localhost:4006/api/`

## Bước 6: Test API

### Test User Registration
```bash
curl -X POST http://localhost:8000/web/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Test Product List
```bash
curl http://localhost:8000/web/products/
```

### Test Home Page Data
```bash
curl http://localhost:8000/web/home/
```

## Khắc phục sự cố

### Lỗi kết nối database
```bash
# Kiểm tra PostgreSQL đang chạy
docker-compose ps postgres

# Xem logs
docker-compose logs postgres
```

### Lỗi port bị chiếm
```bash
# Kiểm tra port nào đang sử dụng
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### Reset database
```bash
# Dừng containers
docker-compose down -v

# Xóa volume
docker volume rm api-gateway_vs_bff_postgres_data

# Khởi động lại
docker-compose up --build
```

## Cấu trúc thư mục

```
api-gateway_vs_bff/
├── api-gateway/           # API Gateway (Port 8000)
├── bff/
│   ├── web-bff/          # Web BFF (Port 3001)
│   └── admin-bff/        # Admin BFF (Port 3002)
├── microservices/
│   ├── user-service/     # User Service (Port 4001)
│   ├── product-service/  # Product Service (Port 4002)
│   ├── order-service/    # Order Service (Port 4003)
│   ├── payment-service/  # Payment Service (Port 4004)
│   ├── inventory-service/# Inventory Service (Port 4005)
│   └── recommendation-service/ # Recommendation Service (Port 4006)
├── frontend/
│   ├── web/              # Web Frontend (HTML/CSS/JS)
│   └── admin/            # Admin Frontend (HTML/CSS/JS)
├── docker-compose.yml    # Docker orchestration
├── .env.example         # Environment variables template
└── README.md            # Project documentation
```

## Tài liệu API

Sau khi khởi động hệ thống, truy cập:
- API Documentation: http://localhost:8000/api/docs/ (Nếu đã cài đặt drf-spectacular)

## Support

Nếu gặp vấn đề, vui lòng check:
1. Docker Desktop đang chạy
2. Tất cả services đã start thành công
3. Database migrations đã chạy
4. Port không bị conflict

## Architecture Flow

```
Browser (Frontend)
    ↓
API Gateway (Port 8000)
    ↓
BFF Layer (Web: 3001, Admin: 3002)
    ↓
Microservices (Ports 4001-4006)
    ↓
PostgreSQL Database (Port 5432)
```

Chúc bạn thành công! 🎉
