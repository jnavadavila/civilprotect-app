@echo off
title CivilProtect Frontend Debugger
echo ==========================================
echo   DIAGNOSTICO Y ARRANQUE DE FRONTEND
echo ==========================================
cd frontend

echo [1/3] Verificando dependencias...
call npm install

echo [2/3] Configurando entorno para Node v22...
set NODE_OPTIONS=--openssl-legacy-provider

echo [3/3] Iniciando Servidor React (Puerto 3000)...
echo Si el navegador no se abre, revisa los errores aqui.
npm start

echo.
echo ==========================================
echo   SI VES ESTO, OCURRIO UN ERROR
echo ==========================================
pause
