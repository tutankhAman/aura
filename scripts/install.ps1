# Check if Python 3.12 is installed
try {
    $pythonVersion = py -3.12 --version
    Write-Host "Found Python version: $pythonVersion"
} catch {
    Write-Host "Python 3.12 not found. Please install Python 3.12 from https://www.python.org/downloads/release/python-3122/"
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "backend\venv")) {
    Write-Host "Creating virtual environment with Python 3.12..."
    py -3.12 -m venv backend\venv
}

# Activate virtual environment and install dependencies
Write-Host "Installing Python dependencies..."
.\backend\venv\Scripts\Activate.ps1

# Upgrade pip first
python -m pip install --upgrade pip

# Install dependencies with error handling
try {
    Write-Host "Installing dependencies..."
    pip install -r requirements.txt
} catch {
    Write-Host "Error installing dependencies. Trying alternative method..."
    pip install --no-cache-dir -r requirements.txt
}

# Install frontend dependencies
Write-Host "Installing frontend dependencies..."
npm install

Write-Host "Installation complete!" 

#.\scripts\start_dev.ps1