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
    Write-Host "`n[✗] Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv backend\venv
    if (-not $?) {
        Write-Host "`n[✗] Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "`n[✓] Virtual environment created successfully" -ForegroundColor Green
}

# Get the full path to Python in the virtual environment
$pythonPath = Join-Path $PWD "backend\venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "`n[✗] Python not found in virtual environment" -ForegroundColor Red
    exit 1
}

# Upgrade pip in the virtual environment
Write-Host "`n[✓] Upgrading pip..." -ForegroundColor Green
& $pythonPath -m pip install --upgrade pip
if (-not $?) {
    Write-Host "`n[✗] Failed to upgrade pip" -ForegroundColor Red
    exit 1
}

# Install requirements if needed
$requirementsPath = Join-Path $PWD "backend\requirements.txt"
if (Test-Path $requirementsPath) {
    Write-Host "`n[✓] Installing Python requirements..." -ForegroundColor Green
    & $pythonPath -m pip install -r $requirementsPath
    if (-not $?) {
        Write-Host "`n[✗] Failed to install requirements" -ForegroundColor Red
        exit 1
    }
}

# Start the FastAPI backend in a new window with a title
$backendCommand = @"
Write-Host '`n[✓] Starting Aura Backend Server...' -ForegroundColor Green
cd '$PWD\backend'
& '$pythonPath' -m uvicorn main:app --reload --port 8000
Write-Host '`n[!] Press any key to close this window...' -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand -WindowStyle Normal

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "`n[✓] Found Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "`n[✗] Node.js not found. Please install Node.js" -ForegroundColor Red
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version
    Write-Host "`n[✓] Found npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "`n[✗] npm not found. Please install npm" -ForegroundColor Red
    exit 1
}

# Install frontend dependencies if needed
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "`n[✓] Installing frontend dependencies..." -ForegroundColor Green
    cd frontend
    npm install
    if (-not $?) {
        Write-Host "`n[✗] Failed to install frontend dependencies" -ForegroundColor Red
        exit 1
    }
    cd ..
} else {
    # Update dependencies if node_modules exists
    Write-Host "`n[✓] Updating frontend dependencies..." -ForegroundColor Green
    cd frontend
    npm install
    if (-not $?) {
        Write-Host "`n[✗] Failed to update frontend dependencies" -ForegroundColor Red
        exit 1
    }
    cd ..
}

# Start the Tauri frontend in the current window
Write-Host "`n[✓] Starting Aura Frontend..." -ForegroundColor Green
cd frontend
npm run tauri dev 