@echo off
echo ===================================================
echo   DESPLIEGUE A PRODUCCION - CIVILPROTECT
echo ===================================================

cd /d "%~dp0"

:: 1. Verificar Certificados
if not exist "nginx_gateway\certs\fullchain.pem" (
    echo [ERROR] No se encontraron certificados SSL en nginx_gateway\certs\
    echo Debes colocar fullchain.pem y privkey.pem antes de desplegar.
    echo Para pruebas locales, puedes generar self-signed certs.
    pause
    exit /b 1
)

:: 2. Build & Up
echo [INFO] Construyendo imagenes y levantando contenedores...
docker compose -f docker-compose.prod.yml up -d --build

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al levantar Docker Compose.
    pause
    exit /b 1
)

:: 3. Esperar a DB (Healthcheck ya lo hace para el backend, pero esperamos para migrar)
echo [INFO] Esperando estabilidad del sistema (15s)...
timeout /t 15 /nobreak >nul

:: 4. Migraciones
echo [INFO] Ejecutando migraciones de base de datos...
docker exec civilprotect-backend-prod alembic upgrade head

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al ejecutar migraciones. Revisa los logs.
) else (
    echo [EXITO] Sistema desplegado y base de datos migrada.
    echo Accede a https://localhost (o tu dominio)
)

pause
