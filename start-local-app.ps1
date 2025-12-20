Write-Host "Starting Cloud Learning Platform (Local Mode)..." -ForegroundColor Cyan

# Define Service Paths
$BaseDir = "c:\Users\PC\OneDrive\Desktop\cloud-learning-platform(needs for GUI)\cloud-learning-platform\cloud-learning-platform\phase2-services\backend-services"
$FrontendDir = "c:\Users\PC\OneDrive\Desktop\cloud-learning-platform(needs for GUI)\cloud-learning-platform\cloud-learning-platform\phase2-services\frontend-web"

# Function to Start a Service
function Start-BackEndService {
    param (
        [string]$Name,
        [string]$Path,
        [int]$Port
    )
    Write-Host "Starting $Name on port $Port..." -ForegroundColor Yellow
    Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "-Command", "cd '$Path'; pip install -r requirements.txt; uvicorn src.api.main:app --port $Port"
}

# Start Backend Services
Start-BackEndService -Name "User Service" -Path "$BaseDir\user-service" -Port 8001
Start-BackEndService -Name "Chat Service" -Path "$BaseDir\chat-service" -Port 8002
Start-BackEndService -Name "Document Service" -Path "$BaseDir\document-service" -Port 8003
Start-BackEndService -Name "Quiz Service" -Path "$BaseDir\quiz-service" -Port 8004
Start-BackEndService -Name "STT Service" -Path "$BaseDir\stt-service" -Port 8005
Start-BackEndService -Name "TTS Service" -Path "$BaseDir\tts-service" -Port 8006

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "-Command", "cd '$FrontendDir'; npm install; npm run dev"

Write-Host "All services started! Access the app at http://localhost:5173" -ForegroundColor Cyan
Write-Host "Press Enter to exit this launcher (services will keep running)..."
Read-Host
