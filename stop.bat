@echo off
REM Stop Script for E-Commerce System

echo ================================================
echo   E-Commerce System - Stopping Services
echo ================================================
echo.

echo [1/2] Stopping Docker Compose services...
docker-compose down

echo.
echo [2/2] Services stopped successfully!
echo.
echo To completely remove data (reset database):
echo   docker-compose down -v
echo   docker volume rm api-gateway_vs_bff_postgres_data
echo.
echo ================================================
pause
