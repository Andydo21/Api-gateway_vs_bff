@echo off
REM Quick Start Script for E-Commerce System

echo ================================================
echo   E-Commerce System - Quick Start
echo   API Gateway + BFF + Microservices
echo ================================================
echo.

echo [1/5] Starting Docker Compose...
docker-compose up -d
echo.

echo Waiting for services to start (30 seconds)...
timeout /t 30 /nobreak
echo.

echo [2/5] Running migrations for all services...
echo.

echo - User Service...
docker-compose exec -T user-service python manage.py makemigrations
docker-compose exec -T user-service python manage.py migrate

echo - Product Service...
docker-compose exec -T product-service python manage.py makemigrations
docker-compose exec -T product-service python manage.py migrate

echo - Order Service...
docker-compose exec -T order-service python manage.py makemigrations
docker-compose exec -T order-service python manage.py migrate

echo - Payment Service...
docker-compose exec -T payment-service python manage.py makemigrations
docker-compose exec -T payment-service python manage.py migrate

echo - Inventory Service...
docker-compose exec -T inventory-service python manage.py makemigrations
docker-compose exec -T inventory-service python manage.py migrate

echo - Recommendation Service...
docker-compose exec -T recommendation-service python manage.py makemigrations
docker-compose exec -T recommendation-service python manage.py migrate

echo.
echo [3/5] Creating sample data...
python create_sample_data.py

echo.
echo [4/5] Starting frontend servers...
start cmd /k "cd frontend\web && python -m http.server 8080"
start cmd /k "cd frontend\admin && python -m http.server 8081"

echo.
echo [5/5] Opening browsers...
timeout /t 3 /nobreak
start http://localhost:8080
start http://localhost:8081/admin.html

echo.
echo ================================================
echo   ✅ System started successfully!
echo ================================================
echo.
echo Services:
echo   - API Gateway:     http://localhost:8000
echo   - Web Frontend:    http://localhost:8080
echo   - Admin Panel:     http://localhost:8081/admin.html
echo.
echo   - Web BFF:         http://localhost:3001
echo   - Admin BFF:       http://localhost:3002
echo.
echo   - User Service:    http://localhost:4001/api/
echo   - Product Service: http://localhost:4002/api/
echo   - Order Service:   http://localhost:4003/api/
echo   - Payment Service: http://localhost:4004/api/
echo   - Inventory Svc:   http://localhost:4005/api/
echo   - Recommend Svc:   http://localhost:4006/api/
echo.
echo Test credentials:
echo   Username: john_doe
echo   Password: password123
echo.
echo To stop all services:
echo   docker-compose down
echo ================================================
echo.
pause
