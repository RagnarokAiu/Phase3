Write-Host "Stopping Cloud Learning Platform Services..." -ForegroundColor Yellow

# Kill Uvicorn (Backend)
$uvicorn = Get-Process uvicorn -ErrorAction SilentlyContinue
if ($uvicorn) {
    Stop-Process -Name uvicorn -Force
    Write-Host "Stopped $($uvicorn.Count) backend services." -ForegroundColor Green
} else {
    Write-Host "No backend services found running." -ForegroundColor Gray
}

# Kill Node (Frontend)
$node = Get-Process node -ErrorAction SilentlyContinue
if ($node) {
    Stop-Process -Name node -Force
    Write-Host "Stopped frontend service." -ForegroundColor Green
} else {
    Write-Host "No frontend service found running." -ForegroundColor Gray
}

Write-Host "All services stopped. You can now run 'start-local-app.ps1' cleanly." -ForegroundColor Cyan
