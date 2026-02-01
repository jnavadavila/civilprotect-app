@echo off
echo [SETUP] Configurando tarea programada para respaldo diario...
echo [INFO] Hora programada: 02:00 AM
echo [INFO] Script: %~dp0backup_daily.bat

:: Requiere permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Este script requiere permisos de Administrador.
    echo Por favor, ejecutalo como Administrador (Click derecho -> Ejecutar como Administrador).
    pause
    exit /b 1
)

schtasks /create /tn "CivilProtectBackup" /tr "\"%~dp0backup_daily.bat\"" /sc daily /st 02:00 /ru SYSTEM /f

if %ERRORLEVEL% EQU 0 (
    echo [EXITO] Tarea programada creada correctamente.
) else (
    echo [ERROR] No se pudo crear la tarea programada.
)

pause
