# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion"
} catch {
    Write-Host "Python not found in PATH. Please install Python and add it to PATH"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "backend\venv")) {
    Write-Host "Virtual environment not found. Please run install.ps1 first"
    exit 1
}

# Get the full path to Python in the virtual environment
$pythonPath = Join-Path $PWD "backend\venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "Python not found in virtual environment. Please run install.ps1 first"
    exit 1
}

# Start the FastAPI backend in a new window with a title
$backendCommand = @"
Write-Host 'Starting Aura Backend Server...' -ForegroundColor Green
cd '$PWD\backend'
& '$pythonPath' -m uvicorn main:app --reload --port 8000
Write-Host 'Press any key to close this window...' -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand -WindowStyle Normal

# Start the Tauri frontend in the current window
Write-Host "Starting Aura Frontend..." -ForegroundColor Green
cd frontend
npm run tauri dev 