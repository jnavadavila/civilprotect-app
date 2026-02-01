Write-Host "Iniciando CivilProtect-AI (Modo Local)..."

# 1. Iniciar Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; Write-Host '>>> INSTALANDO DEPENDENCIAS BACKEND...'; pip install -r requirements.txt; Write-Host '>>> INICIANDO SERVIDOR BACKEND (Puerto 8000)...'; uvicorn main:app --reload --port 8000"

# 2. Iniciar Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; Write-Host '>>> INSTALANDO DEPENDENCIAS FRONTEND (Puede tardar unos minutos)...'; npm install; Write-Host '>>> INICIANDO CLIENTE REACT (Puerto 3000)...'; npm start"

Write-Host "Se han abierto dos ventanas segundarias para el Backend y Frontend."
