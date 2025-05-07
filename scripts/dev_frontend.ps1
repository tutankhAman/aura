# Check if frontend directory exists
if (-not (Test-Path "frontend")) {
    Write-Host "Frontend directory not found. Please run setup_frontend.ps1 first" -ForegroundColor Red
    exit 1
}

# Start the Tauri frontend
Write-Host "Starting Aura Frontend..." -ForegroundColor Green
cd frontend
npm run tauri dev 