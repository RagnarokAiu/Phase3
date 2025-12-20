Write-Host "Installing dependencies for ALL services..." -ForegroundColor Cyan

$BaseDir = "c:\Users\PC\OneDrive\Desktop\cloud-learning-platform(needs for GUI)\cloud-learning-platform\cloud-learning-platform\phase2-services\backend-services"

function Install-Reqs {
    param ([string]$Name, [string]$Path)
    Write-Host "Installing requirements for $Name..." -ForegroundColor Yellow
    Push-Location $Path
    try {
        python -m pip install -r requirements.txt
    } catch {
        Write-Host "Failed to install requirements for $Name" -ForegroundColor Red
    }
    Pop-Location
}

Install-Reqs -Name "User Service" -Path "$BaseDir\user-service"
Install-Reqs -Name "Chat Service" -Path "$BaseDir\chat-service"
Install-Reqs -Name "Document Service" -Path "$BaseDir\document-service"
Install-Reqs -Name "Quiz Service" -Path "$BaseDir\quiz-service"
Install-Reqs -Name "STT Service" -Path "$BaseDir\stt-service"
Install-Reqs -Name "TTS Service" -Path "$BaseDir\tts-service"

Write-Host "Stopping any running services..." -ForegroundColor Red
Stop-Process -Name uvicorn -Force -ErrorAction SilentlyContinue
Stop-Process -Name node -Force -ErrorAction SilentlyContinue

Write-Host "Starting Application..." -ForegroundColor Green
& "c:\Users\PC\OneDrive\Desktop\cloud-learning-platform(needs for GUI)\cloud-learning-platform\cloud-learning-platform\phase2-services\start-local-app.ps1"
