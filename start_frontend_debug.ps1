Write-Host "Re-intentando iniciar solo el Frontend..."
cd frontend
# Forzar una instalación rápida si falta algo
if (!(Test-Path "node_modules")) {
    Write-Host "Instalando dependencias (esto tardará)..."
    npm install
}
Write-Host "Iniciando React..."
# Usar cmd /c start para abrir ventana visible y que no muera el proceso
cmd /c start "CivilProtect Frontend" npm start
