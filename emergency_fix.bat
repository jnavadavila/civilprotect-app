@echo off
echo [1/4] Deteniendo procesos zombies...
taskkill /F /IM python.exe /T 2>NUL
taskkill /F /IM node.exe /T 2>NUL
taskkill /F /IM npm.exe /T 2>NUL

echo [2/4] Verificando puertos libres...
timeout /t 2 /nobreak >NUL

echo [3/4] Iniciando Backend (Log: backend.log)...
cd backend
start /B python main.py > backend.log 2>&1
if %errorlevel% neq 0 (
    echo ERROR al iniciar backend
    pause
    exit /b
)
cd ..

echo [4/4] Iniciando Frontend (Log: frontend.log)...
cd frontend
echo Espere mientras se compila el frontend...
start /B npm start > frontend.log 2>&1
cd ..

echo ====================================================
echo SISTEMA REINICIADO. POR FAVOR ESPERE 15 SEGUNDOS
echo Y LUEGO RECARGUE: http://localhost:3000
echo ====================================================
