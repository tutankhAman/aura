# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "Found Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version
    Write-Host "Found npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "npm not found. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
cd frontend

# Install npm dependencies
try {
    npm install
    Write-Host "Frontend dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error installing npm dependencies. Trying alternative method..." -ForegroundColor Yellow
    npm install --force
    Write-Host "Frontend dependencies installed successfully!" -ForegroundColor Green
}

# Check if Tauri CLI is installed
try {
    $tauriVersion = npm list @tauri-apps/cli
    Write-Host "Tauri CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "Installing Tauri CLI..." -ForegroundColor Yellow
    npm install -D @tauri-apps/cli
}

Write-Host "Frontend setup complete!" -ForegroundColor Green 