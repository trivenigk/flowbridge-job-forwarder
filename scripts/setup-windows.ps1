# FlowBridge - Windows Setup Script
# Run in PowerShell: .\setup-windows.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  FlowBridge - Windows Auto Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker
Write-Host "[1/7] Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "  OK: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Docker not installed" -ForegroundColor Red
    Write-Host "  Download: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Step 2: Check Docker running
Write-Host "[2/7] Checking Docker Desktop is running..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "  OK: Docker Desktop running" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Docker Desktop not running. Start it and rerun script." -ForegroundColor Red
    exit 1
}

# Step 3: Project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
Write-Host "[3/7] Project dir: $projectRoot" -ForegroundColor Green

# Step 4: Create folders
Write-Host "[4/7] Creating folders..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "$projectRoot\setup" | Out-Null
New-Item -ItemType Directory -Force -Path "$projectRoot\chrome-profile" | Out-Null
Write-Host "  OK: setup/ and chrome-profile/ ready" -ForegroundColor Green

# Step 5: .env file
Write-Host "[5/7] Configuring .env..." -ForegroundColor Yellow
$envPath = "$projectRoot\.env"
if (-not (Test-Path $envPath)) {
    $sheetId = Read-Host "  Enter your Google Sheet ID"
    $envContent = @"
GOOGLE_SHEET_ID=$sheetId
CHROME_PROFILE_PATH=/app/chrome-profile
"@
    Set-Content -Path $envPath -Value $envContent
    Write-Host "  OK: .env created" -ForegroundColor Green
} else {
    Write-Host "  SKIP: .env already exists" -ForegroundColor Gray
}

# Step 6: credentials.json check
Write-Host "[6/7] Checking credentials.json..." -ForegroundColor Yellow
$credPath = "$projectRoot\setup\credentials.json"
if (-not (Test-Path $credPath)) {
    Write-Host "  MISSING: setup\credentials.json" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Download from Google Cloud Console:" -ForegroundColor Yellow
    Write-Host "  1. Go to https://console.cloud.google.com" -ForegroundColor White
    Write-Host "  2. APIs and Services -> Credentials" -ForegroundColor White
    Write-Host "  3. Create OAuth 2.0 Client ID (Desktop app)" -ForegroundColor White
    Write-Host "  4. Download JSON" -ForegroundColor White
    Write-Host "  5. Save to: $credPath" -ForegroundColor White
    Write-Host ""
    Read-Host "  Press Enter once credentials.json is in place"
    if (-not (Test-Path $credPath)) {
        Write-Host "  ERROR: credentials.json still missing. Exit." -ForegroundColor Red
        exit 1
    }
}
Write-Host "  OK: credentials.json found" -ForegroundColor Green

# Step 7: Build and start
Write-Host "[7/7] Building and starting container..." -ForegroundColor Yellow
docker compose build
docker compose up -d
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  SUCCESS: FlowBridge running!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. First-time WhatsApp login:" -ForegroundColor White
Write-Host "     - Download VNC viewer: https://www.realvnc.com/en/connect/download/viewer/" -ForegroundColor White
Write-Host "     - Connect to: localhost:5900 (no password)" -ForegroundColor White
Write-Host "     - Scan QR code with your phone" -ForegroundColor White
Write-Host ""
Write-Host "  2. View logs: docker compose logs -f" -ForegroundColor White
Write-Host "  3. Stop: docker compose down" -ForegroundColor White
Write-Host "  4. Restart: docker compose restart" -ForegroundColor White
Write-Host ""
