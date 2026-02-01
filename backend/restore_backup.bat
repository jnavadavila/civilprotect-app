@echo off
setlocal
cd /d "%~dp0"

set "BACKUP_FILE=%~1"
if "%BACKUP_FILE%"=="" (
    echo [ERROR] Uso: restore_backup.bat "ruta\al\archivo_backup.sql"
    echo Puedes arrastrar el archivo .sql sobre este script.
    pause
    exit /b 1
)

echo =================================================================
echo                 ADVERTENCIA DE RESTAURACION
echo =================================================================
echo.
echo Se restaurara la base de datos 'civilprotect_dev' desde el archivo:
echo %BACKUP_FILE%
echo.
echo [PELIGRO] Los datos actuales en la base de datos podrian ser SOBREESCRITOS.
echo.
echo =================================================================
set /p CONFIRM="Escribe 'CONFIRMAR' (mayusculas) para proceder: "

if not "%CONFIRM%"=="CONFIRMAR" (
    echo [CANCELADO] Operacion abortada por el usuario.
    pause
    exit /b 1
)

echo.
echo [1/2] Deteniendo conexiones activas (opcional)...
:: En entornos docker dev usualmente no es critico, pero es buena practica.

echo [2/2] Restaurando base de datos desde SQL...
:: Usamos 'type' para enviar el contenido al stdin del comando docker exec
type "%BACKUP_FILE%" | docker exec -i civilprotect_pg psql -U user -d civilprotect_dev

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [EXITO] Restauracion completada correctamente.
) else (
    echo.
    echo [ERROR] Fallo durante la restauracion. Verifica el log.
)

pause
endlocal
