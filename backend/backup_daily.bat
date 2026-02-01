@echo off
setlocal
cd /d "%~dp0"

set "BACKUP_DIR=%~dp0backups"
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: Obtener fecha en formato YYYY-MM-DD (Independiente de la config regional)
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "DATE_STR=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%"
set "TIME_STR=%datetime:~8,2%-%datetime:~10,2%"

set "FILENAME=%BACKUP_DIR%\civilprotect_backup_%DATE_STR%_%TIME_STR%.sql"

echo [BACKUP] Iniciando respaldo de base de datos a: %FILENAME%
echo [INFO] Contenedor: civilprotect_pg
echo [INFO] Base de datos: civilprotect_dev

:: Ejecutar pg_dump dentro del contenedor
docker exec civilprotect_pg pg_dump -U user civilprotect_dev > "%FILENAME%"

if %ERRORLEVEL% EQU 0 (
    echo [EXITO] Respaldo completado correctamente.
) else (
    echo [ERROR] Fallo al crear el respaldo. Verifica que el contenedor este corriendo.
    exit /b 1
)

:: Rotación de Backups: Eliminar archivos .sql con antigüedad mayor a 30 días
echo [INFO] Eliminando respaldos antiguos (>30 dias)...
forfiles /p "%BACKUP_DIR%" /s /m *.sql /d -30 /c "cmd /c del @path & echo [BORRADO] @path" 2>nul

endlocal
