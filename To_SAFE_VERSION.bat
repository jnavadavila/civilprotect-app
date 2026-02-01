@echo off
echo ========================================================
echo   BLINDAJE DE VERSION - CIVILPROTECT
echo ========================================================

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado en PATH. Requerido para el script de backup.
    pause
    exit /b 1
)

echo [INFO] Ejecutando script de respaldo inteligente...
python tools/backup_source.py

if %errorlevel% equ 0 (
    echo.
    echo [EXITO] La version ha sido salvada y blindada.
) else (
    echo [ERROR] Hubo un problema durante el respaldo.
)

pause
