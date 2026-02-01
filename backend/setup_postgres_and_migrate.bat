@echo off
echo [SETUP] Iniciando configuracion de PostgreSQL para CivilProtect...

cd /d "%~dp0"

echo [1/4] Levantando contenedor Docker...
docker compose -f docker-compose.db.yml up -d
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] No se pudo iniciar Docker. Asegurate de tener Docker Desktop corriendo.
    echo Si deseas usar PostgreSQL local (sin Docker), asegurate de que el servicio este corriendo en el puerto 5432.
    pause
    exit /b 1
)

echo [2/4] Esperando a que la base de datos este lista (10s)...
timeout /t 10 /nobreak >nul

echo [3/4] Generando migracion inicial con Alembic...
alembic revision --autogenerate -m "initial schema"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al generar migracion. Verifica la conexion a la BD.
    pause
    exit /b 1
)

echo [4/4] Aplicando migraciones...
alembic upgrade head
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo al aplicar migraciones.
    pause
    exit /b 1
)

echo [EXITO] Base de datos PostgreSQL configurada y migrada correctamente.
pause
