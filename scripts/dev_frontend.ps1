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

# Check if frontend directory exists
if (-not (Test-Path "frontend")) {
    Write-Host "`n[✗] Frontend directory not found" -ForegroundColor Red
    exit 1
}

# Check if node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "`n[!] Frontend dependencies not found. Installing..." -ForegroundColor Yellow
    cd frontend
    npm install
    if (-not $?) {
        Write-Host "`n[✗] Failed to install frontend dependencies" -ForegroundColor Red
        exit 1
    }
    cd ..
}

# Start the Tauri frontend
Write-Host "`n[✓] Starting Aura Frontend..." -ForegroundColor Green
cd frontend
npm run tauri dev 