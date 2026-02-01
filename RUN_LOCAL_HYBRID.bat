@echo off
setlocal
title CivilProtect AI - MODO LOCAL DIRECTO
echo ==================================================
echo   CIVILPROTECT - MODO EMERGENCIA SIN DOCKER
echo ==================================================
echo.
echo Detectamos problemas con Docker. Iniciando modo nativo...
echo.

:: 1. Verificaciones
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no esta en el PATH.
    pause
    exit /b 1
)
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js/NPM no esta en el PATH.
    pause
    exit /b 1
)

:: 2. Backend
echo [1/3] Iniciando Backend Python...
cd backend

:: Forzar uso de SQLite para local
if not exist .env copy .env.example .env >nul
findstr "DATABASE_URL=sqlite" .env >nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Configurando para usar SQLite Local...
    echo. >> .env
    echo # Override para modo local >> .env
    echo DATABASE_URL=sqlite:///./data/civilprotect.db >> .env
)

:: Instalar dependencias si faltan (rapido)
pip install -r requirements.txt >nul 2>nul

:: Lanzar Backend en ventana separada para ver logs
start "CivilProtect Backend API" cmd /k "uvicorn main:app --reload --port 8000"
echo Backend iniciado puerto 8000.
cd ..

:: 3. Frontend
echo [2/3] Iniciando Frontend React...
cd frontend
if not exist .env echo REACT_APP_API_URL=http://localhost:8000 > .env
 
:: check node_modules
if not exist node_modules echo [INFO] Instalando librerias React... & call npm install >nul

echo [3/3] LANZANDO APLICACION...
echo.
echo Por favor espera a que se abra el navegador...
echo Si cierra esta ventana, se detendra el Frontend.
echo.
npm start
