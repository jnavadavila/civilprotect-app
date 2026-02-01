@echo off
echo ========================================================
echo   CONFIGURACION AUTOMATICA DE SSL (Let's Encrypt)
echo ========================================================
echo.
echo Este script solicitara un certificado SSL real para tu dominio.
echo Requisitos:
echo 1. El dominio debe apuntar a la IP publica de este servidor.
echo 2. El puerto 80 debe estar abierto.
echo 3. Nginx debe estar corriendo (RUN_PRODUCTION_DEPLOY.bat ya ejecutado).
echo.

set /p DOMAIN="Ingresa tu dominio (ej. app.civilprotect.com): "
set /p EMAIL="Ingresa tu email para notificaciones de renovacion: "

if "%DOMAIN%"=="" goto error
if "%EMAIL%"=="" goto error

:: Asegurar directorios
if not exist "nginx_gateway\www" mkdir "nginx_gateway\www"

echo.
echo [1/2] Solicitando certificado para %DOMAIN%...
docker compose -f docker-compose.prod.yml run --rm certbot certonly ^
    --webroot ^
    --webroot-path /var/www/certbot ^
    --email %EMAIL% ^
    --agree-tos ^
    --no-eff-email ^
    -d %DOMAIN%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Certbot fallo. Verificaste que el dominio apunta aqui?
    echo Nota: Si estas en localhost, esto fallara (Let's Encrypt requiere dominio publico).
    pause
    exit /b 1
)

echo.
echo [2/2] Recargando Nginx...
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo.
echo [EXITO] HTTPS configurado correctamente para https://%DOMAIN%
pause
exit /b 0

:error
echo [ERROR] Debes ingresar dominio y email.
pause
exit /b 1
