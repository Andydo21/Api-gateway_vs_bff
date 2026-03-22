@echo off
echo ================================================
echo   Clearing Redis Data for E-Commerce System
echo ================================================
echo.

echo [1/2] Checking if Redis container is running...
docker ps | findstr redis > nul
if errorlevel 1 (
    echo [ERROR] Redis container is not running! Please start the system first using start.bat
    echo.
    pause
    exit /b
)

echo [2/2] Clearing all data in Redis...
docker-compose exec -T redis redis-cli FLUSHALL
echo.

echo ================================================
echo   ✅ Redis Data cleared successfully!
echo ================================================
echo.
pause
