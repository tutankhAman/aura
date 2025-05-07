# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found in PATH. Please install Python and add it to PATH" -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "backend\venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv backend\venv
}

# Activate virtual environment and install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
.\backend\venv\Scripts\Activate.ps1

# Upgrade pip first
python -m pip install --upgrade pip

# Install dependencies with error handling
try {
    pip install -r requirements.txt
    Write-Host "Backend dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error installing dependencies. Trying alternative method..." -ForegroundColor Yellow
    pip install --no-cache-dir -r requirements.txt
    Write-Host "Backend dependencies installed successfully!" -ForegroundColor Green
}

Write-Host "Backend setup complete!" -ForegroundColor Green 