# MediStore AI - Start All Services
Write-Host "Starting MediStore AI..." -ForegroundColor Cyan

$root = $PSScriptRoot

# Start V2 Backend (port 8000)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; .\venv\Scripts\activate; uvicorn server:app --reload --port 8000"

# Start V3 Backend (port 8001)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; .\venv\Scripts\activate; uvicorn server_v3:app --reload --port 8001"

# Start Frontend (port 5173)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev"

Write-Host ""
Write-Host "All services starting in separate windows!" -ForegroundColor Green
Write-Host "  - V2 Backend : http://localhost:8000" -ForegroundColor Yellow
Write-Host "  - V3 Backend : http://localhost:8001" -ForegroundColor Yellow
Write-Host "  - Frontend   : http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "Open your browser at: http://localhost:5173" -ForegroundColor Cyan
