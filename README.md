# API Gateway + BFF + Microservices với Django & HTML

Hệ thống e-commerce hoàn chỉnh với kiến trúc hiện đại sử dụng Django.

## 🚀 Quick Start

### Cách nhanh nhất (Windows)
```bat
# Clone và chạy
cd d:\Django_project\api-gateway_vs_bff
start.bat
```

### Manual Start
```bash
# 1. Start services
docker-compose up --build

# 2. Run migrations (in new terminal)
docker-compose exec user-service python manage.py migrate
docker-compose exec product-service python manage.py migrate
docker-compose exec order-service python manage.py migrate
docker-compose exec payment-service python manage.py migrate
docker-compose exec inventory-service python manage.py migrate
docker-compose exec recommendation-service python manage.py migrate

# 3. Create sample data
python create_sample_data.py

# 4. Open frontend
start http://localhost:8080
```

📖 **Chi tiết xem file [SETUP_GUIDE.md](SETUP_GUIDE.md)**

## Kiến trúc tổng thể

```
Client Layer
├── Web App (HTML/CSS/JS)
└── Admin Panel (HTML/CSS/JS)
        ↓
API Gateway (Django)
        ↓
BFF Layer (Django)
├── Web BFF
└── Admin BFF
        ↓
Microservices (Django)
├── User Service
├── Product Service
├── Order Service
├── Payment Service
├── Inventory Service
└── Recommendation Service
        ↓
Database (PostgreSQL)
```

## Cấu trúc thư mục

```
.
├── api-gateway/              # Django API Gateway
├── bff/                      # Backend for Frontend
│   ├── web-bff/             # Django Web BFF
│   └── admin-bff/           # Django Admin BFF
├── microservices/            # Django Microservices
│   ├── user-service/
│   ├── product-service/
│   ├── order-service/
│   ├── payment-service/
│   ├── inventory-service/
│   └── recommendation-service/
├── frontend/                 # HTML Frontend
│   ├── web/                 # Web application
│   └── admin/               # Admin panel
├── shared/                   # Shared utilities
└── docker-compose.yml        # Docker orchestration
```

## Khởi động hệ thống

### Cách 1: Docker (Khuyên dùng)
```bash
docker-compose up -d
```

### Cách 2: Manual (Development)
```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
.\venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy migrations
python manage.py migrate

# Khởi động services (mở terminal riêng cho mỗi service)
cd api-gateway && python manage.py runserver 8000
cd bff/web-bff && python manage.py runserver 3001
cd bff/admin-bff && python manage.py runserver 3002
cd microservices/user-service && python manage.py runserver 4001
cd microservices/product-service && python manage.py runserver 4002
cd microservices/order-service && python manage.py runserver 4003
cd microservices/payment-service && python manage.py runserver 4004
cd microservices/inventory-service && python manage.py runserver 4005
cd microservices/recommendation-service && python manage.py runserver 4006
```

## Endpoints

### API Gateway
- **Port**: 8000
- `/web/*` → Web BFF (3001)
- `/admin/*` → Admin BFF (3002)

### BFF Services
- **Web BFF**: http://localhost:3001
- **Admin BFF**: http://localhost:3002

### Microservices
- **User Service**: http://localhost:4001
- **Product Service**: http://localhost:4002
- **Order Service**: http://localhost:4003
- **Payment Service**: http://localhost:4004
- **Inventory Service**: http://localhost:4005
- **Recommendation Service**: http://localhost:4006

### Frontend
- **Web App**: http://localhost:8000/web/
- **Admin Panel**: http://localhost:8000/admin/

### Database
- **PostgreSQL**: localhost:5432

## Công nghệ sử dụng

- **Backend Framework**: Django 5.0, Django REST Framework
- **API Gateway**: Django với custom routing
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: PostgreSQL
- **ORM**: Django ORM
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Containerization**: Docker, Docker Compose

## Features

### API Gateway
- Routing tới BFF services
- Authentication/Authorization
- Rate Limiting
- Logging & Monitoring
- CORS handling

### BFF Layer
- Client-specific API optimization
- Request aggregation từ nhiều microservices
- Response transformation
- API composition

### Microservices
- Independent deployment
- Scalability
- Business logic isolation
- Database per service pattern

## Development

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Tạo migrations
python manage.py makemigrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Chạy development server
python manage.py runserver

# Chạy tests
python manage.py test
```

## License
MIT
