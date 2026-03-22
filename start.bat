@echo off
REM Quick Start Script for Pitch-Booking & Startup Ecosystem
REM API Gateway (APISIX) + BFF + Microservices

echo ================================================
echo   Pitch-Booking System - Quick Start
echo   Apache APISIX + BFF + Microservices
echo ================================================
echo.

echo [1/4] Starting Docker Compose...
docker-compose up -d --build
echo.

echo Waiting for services to start (20 seconds)...
timeout /t 20 /nobreak
echo.

echo [2/4] Running migrations for all services...
echo.

set SERVICES=user-service startup-service scheduling-service booking-service meeting-service feedback-service funding-service resource-service matchmaking-service notification-service

for %%s in (%SERVICES%) do (
    echo - %%s...
    docker-compose exec -T %%s python manage.py migrate --noinput
)

echo.
echo [3/4] Configuring APISIX Gateway Routes...
python setup_apisix_routes.py

echo.
echo [4/4] Opening Web Interface...
timeout /t 5 /nobreak
start http://localhost/ui/

echo.
echo ================================================
echo   ✅ System started successfully!
echo ================================================
echo.
echo Access URLs:
echo   - App UI:          http://localhost/ui/
echo   - Admin Panel:     http://localhost/admin-ui/admin.html
echo   - APISIX Dashboard: http://localhost:9000 (admin/password)
echo.
echo To stop all services:
echo   docker-compose down
echo ================================================
echo.
pause
