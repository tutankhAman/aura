# Check if Python 3.12 is installed
try {
    $pythonVersion = py -3.12 --version
    Write-Host "`n[✓] Found Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "`n[✗] Python 3.12 not found. Please install Python 3.12 from https://www.python.org/downloads/release/python-3122/" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "`n[✓] Found Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "`n[✗] Node.js not found. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
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

# Create virtual environment if it doesn't exist
if (-not (Test-Path "backend\venv")) {
    Write-Host "`n[✓] Creating virtual environment with Python 3.12..." -ForegroundColor Green
    py -3.12 -m venv backend\venv
    if (-not $?) {
        Write-Host "`n[✗] Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment and install dependencies
Write-Host "`n[✓] Activating virtual environment..." -ForegroundColor Green
.\backend\venv\Scripts\Activate.ps1
if (-not $?) {
    Write-Host "`n[✗] Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Upgrade pip first
Write-Host "`n[✓] Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip
if (-not $?) {
    Write-Host "`n[✗] Failed to upgrade pip" -ForegroundColor Red
    exit 1
}

# Install Python dependencies with error handling
Write-Host "`n[✓] Installing Python dependencies..." -ForegroundColor Green
try {
    pip install -r backend\requirements.txt
    if (-not $?) {
        throw "Failed to install dependencies"
    }
} catch {
    Write-Host "`n[!] Error installing dependencies. Trying alternative method..." -ForegroundColor Yellow
    try {
        pip install --no-cache-dir -r backend\requirements.txt
        if (-not $?) {
            throw "Failed to install dependencies with alternative method"
        }
    } catch {
        Write-Host "`n[✗] Failed to install Python dependencies" -ForegroundColor Red
        exit 1
    }
}

# Install frontend dependencies
Write-Host "`n[✓] Installing frontend dependencies..." -ForegroundColor Green
cd frontend
try {
    npm install
    if (-not $?) {
        throw "Failed to install frontend dependencies"
    }
} catch {
    Write-Host "`n[✗] Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}
cd ..

Write-Host "`n[✓] Installation complete!" -ForegroundColor Green
Write-Host "`n[!] You can now run the development environment using: .\scripts\start_dev.ps1" -ForegroundColor Yellow