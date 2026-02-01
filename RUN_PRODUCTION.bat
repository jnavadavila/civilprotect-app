@echo off
echo ==================================================
echo   CIVILPROTECT AI - PRODUCTION LAUNCHER
echo ==================================================
echo.
echo [1/3] Cargando configuracion de entorno...
if not exist backend\.env copy backend\.env.example backend\.env
if not exist frontend\.env copy frontend\.env.example frontend\.env

echo [2/3] Construyendo contenedores optimizados (Nginx + Gunicorn)...
docker-compose -f docker-compose.prod.yml build

echo [3/3] Iniciando Sistema...
docker-compose -f docker-compose.prod.yml up -d

echo.
echo ==================================================
echo   SISTEMA OPERATIVO
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000/docs
echo ==================================================
pause
