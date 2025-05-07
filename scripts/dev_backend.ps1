# Check if virtual environment exists
if (-not (Test-Path "backend\venv")) {
    Write-Host "Virtual environment not found. Please run setup_backend.ps1 first" -ForegroundColor Red
    exit 1
}

# Start the FastAPI backend
Write-Host "Starting Aura Backend Server..." -ForegroundColor Green
cd backend

# Activate virtual environment and show activation
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
Write-Host "Virtual environment activated: $(Get-Location)\venv" -ForegroundColor Green

# Start the server
Write-Host "Server running at http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
python -m uvicorn main:app --reload --port 8000 