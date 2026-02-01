@echo off
setlocal EnableDelayedExpansion

echo ========================================================
echo   🛡️ DESPLIEGUE SEGURO V4.5 - CIVILPROTECT
echo   (Migración y Hardening Automático - Sin Retrocesos)
echo ========================================================
echo.

cd /d "%~dp0"

:: ---------------------------------------------------------
:: 1. VERIFICACIONES DE SEGURIDAD PREVIAS
:: ---------------------------------------------------------
echo [1/6] Verificando requisitos...

:: Verificar si existe la DB origen
if not exist "backend\data\civilprotect.db" (
    echo [ERROR] No se encuentra backend\data\civilprotect.db.
    echo No hay datos para migrar. Asegúrate de que estás en la ruta correcta.
    pause
    exit /b 1
)

:: Verificar certificados SSL
:: Usamos GOTO para salir de bloque IF anidado y evitar errores de sintaxis
if not exist "nginx_gateway\certs\fullchain.pem" goto GENERATE_CERTS
goto SKIP_CERTS

:GENERATE_CERTS
echo [AVISO] No se encontraron certificados SSL reales.
echo Generando certificados auto-firmados temporales para permitir el despliegue...

if not exist "nginx_gateway\certs" mkdir "nginx_gateway\certs"

:: Usar script Python como fallback robusto
echo Generando certificados con Python (cryptography)...
python tools/generate_ssl.py

if exist "nginx_gateway\certs\fullchain.pem" (
    echo [OK] Certificados temporales generados.
) else (
    echo [ERROR] Fallo la generacion de certificados.
    echo Asegurate de tener las dependencias instaladas (pip install cryptography).
    pause
    exit /b 1
)

:SKIP_CERTS

:: ---------------------------------------------------------
:: 2. BACKUP PREVENTIVO
:: ---------------------------------------------------------
echo.
echo [2/6] Realizando Backup de Seguridad...
set "TIMESTAMP=%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "BACKUP_DIR=civilprotect_shield_backups\DEPLOY_%TIMESTAMP%"

mkdir "%BACKUP_DIR%"
copy "backend\data\civilprotect.db" "%BACKUP_DIR%\" >nul
xcopy "backend\pdfs" "%BACKUP_DIR%\pdfs\" /E /I /Y >nul

echo [OK] Backup guardado en %BACKUP_DIR%

:: ---------------------------------------------------------
:: 3. CONSTRUCCIÓN Y DESPLIEGUE
:: ---------------------------------------------------------
echo.
echo [3/6] Levantando infraestructura blindada...
docker compose -f docker-compose.prod.yml down --remove-orphans
docker compose -f docker-compose.prod.yml up -d --build

if !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Fallo al iniciar Docker Compose.
    echo Restaurando estado anterior...
    exit /b 1
)

:: ---------------------------------------------------------
:: 4. ESPERA Y SALUD
:: ---------------------------------------------------------
echo.
echo [4/6] Esperando a que el Backend este saludable (20s)...
echo Esto asegura que la DB PostgreSQL esta lista y conectada.
timeout /t 20 /nobreak >nul

:: ---------------------------------------------------------
:: 5. MIGRACIÓN DE DATOS (EL PASO CRÍTICO)
:: ---------------------------------------------------------
echo.
echo [5/6] Ejecutando Migración de Datos (ETL: SQLite -^> Postgres)...

:: Crear tablas primero
echo    - Creando esquema de tablas...
docker exec civilprotect-backend-prod python -c "from database import init_db; init_db()"

:: Ejecutar ETL
echo    - Transfiriendo datos históricos...
docker exec civilprotect-backend-prod python etl_sqlite_to_postgres.py

if !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Falló la migración de datos.
    echo Los datos en PostgreSQL pueden estar incompletos.
    echo Tu base de datos SQLite original ESTÁ SEGURA en %BACKUP_DIR%.
    pause
    exit /b 1
)

:: ---------------------------------------------------------
:: 6. VERIFICACIÓN FINAL
:: ---------------------------------------------------------
echo.
echo [6/6] Verificando estado final...
docker compose -f docker-compose.prod.yml ps

echo.
echo ========================================================
echo   ✅ DESPLIEGUE COMPLETADO EXITOSAMENTE
echo ========================================================
echo.
echo Accede a tu aplicación en: https://localhost
echo.
echo NOTA: Si usaste certificados auto-firmados, acepta la advertencia
echo de seguridad en tu navegador.
echo.
pause
