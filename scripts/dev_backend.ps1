# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "`n[✓] Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "`n[✗] Python not found in PATH. Please install Python and add it to PATH" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "backend\venv")) {
    Write-Host "`n[✗] Virtual environment not found. Please run install.ps1 first" -ForegroundColor Red
    exit 1
}

# Get the full path to Python in the virtual environment
$pythonPath = Join-Path $PWD "backend\venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "`n[✗] Python not found in virtual environment" -ForegroundColor Red
    exit 1
}

# Start the FastAPI backend
Write-Host "`n[✓] Starting Aura Backend Server..." -ForegroundColor Green
cd backend

# Activate virtual environment and show activation
Write-Host "`n[✓] Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1
if (-not $?) {
    Write-Host "`n[✗] Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Start the server
Write-Host "`n[✓] Server running at http://localhost:8000" -ForegroundColor Green
Write-Host "`n[!] Press Ctrl+C to stop the server" -ForegroundColor Yellow
& $pythonPath -m uvicorn main:app --reload --port 8000 