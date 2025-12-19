# Quick Setup Script for Windows
# Run this script to set up the project quickly

Write-Host "Setting up Organization Management System..." -ForegroundColor Green

# Check Python installation
Write-Host "`n📌 Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version
    Write-Host "$pythonVersion found" -ForegroundColor Green
}
catch {
    Write-Host "Python not found. Please install Python 3.9+ first." -ForegroundColor Red
    exit 1
}

# Check MongoDB installation
Write-Host "`n📌 Checking MongoDB..." -ForegroundColor Cyan
$mongoRunning = Get-Process mongod -ErrorAction SilentlyContinue
if ($mongoRunning) {
    Write-Host "MongoDB is running" -ForegroundColor Green
}
else {
    Write-Host "MongoDB is not running. Please start MongoDB before running the app." -ForegroundColor Yellow
}

# Create virtual environment
Write-Host "`n📌 Creating virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists. Skipping..." -ForegroundColor Yellow
}
else {
    python -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n📌 Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "`n📌 Installing dependencies..." -ForegroundColor Cyan
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Dependencies installed" -ForegroundColor Green

# Create .env file if it doesn't exist
Write-Host "`n📌 Setting up environment configuration..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host ".env file already exists. Skipping..." -ForegroundColor Yellow
}
else {
    Copy-Item ".env.example" ".env"
    Write-Host ".env file created from .env.example" -ForegroundColor Green
    Write-Host "IMPORTANT: Update SECRET_KEY in .env file for production!" -ForegroundColor Yellow
}

# Generate a secure secret key
Write-Host "`n📌 Generating secure SECRET_KEY..." -ForegroundColor Cyan
$secretKey = python -c "import secrets; print(secrets.token_hex(32))"
Write-Host "Generated SECRET_KEY: $secretKey" -ForegroundColor Green
Write-Host "   Copy this to your .env file!" -ForegroundColor Yellow

# Summary
Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Update SECRET_KEY in .env file with the generated key above" -ForegroundColor White
Write-Host "   2. Ensure MongoDB is running: mongod" -ForegroundColor White
Write-Host "   3. Run the application: uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "   4. Open API docs: http://localhost:8000/docs" -ForegroundColor White

Write-Host "`n🎯 Quick Start Commands:" -ForegroundColor Cyan
Write-Host "   # Start the server" -ForegroundColor Gray
Write-Host "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
Write-Host "`n   # View API documentation" -ForegroundColor Gray
Write-Host "   Start-Process http://localhost:8000/docs" -ForegroundColor Yellow

Write-Host "`n📚 Documentation:" -ForegroundColor Cyan
Write-Host "   - README.md: Complete setup and architecture guide" -ForegroundColor White
Write-Host "   - API_EXAMPLES.md: Example API requests and responses" -ForegroundColor White



Write-Host "`n"
