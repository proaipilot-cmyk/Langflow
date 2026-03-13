#!/usr/bin/env pwsh
# Resume Analyzer RAG - Quick Start Script (PowerShell)
# Run with: .\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "     Resume Analyzer RAG - Quick Start" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Check if UV is installed
try {
    $uvVersion = uv --version 2>$null
    Write-Host "[OK] UV is installed: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] UV is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install UV first:" -ForegroundColor Yellow
    Write-Host "  pipx install uv" -ForegroundColor White
    Write-Host "  OR" -ForegroundColor White
    Write-Host "  pip install uv" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Step 1: Create virtual environment
Write-Host "[1/5] Creating virtual environment..." -ForegroundColor Cyan
uv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Virtual environment created" -ForegroundColor Green

# Step 2: Activate virtual environment
Write-Host ""
Write-Host "[2/5] Activating virtual environment..." -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"
Write-Host "[OK] Virtual environment activated" -ForegroundColor Green

# Step 3: Install dependencies
Write-Host ""
Write-Host "[3/5] Installing dependencies..." -ForegroundColor Cyan
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# Step 4: Run connectivity tests
Write-Host ""
Write-Host "[4/5] Running connectivity tests..." -ForegroundColor Cyan
uv run python test_connections.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Some tests failed - check .env file" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please ensure you have created a .env file with:" -ForegroundColor Yellow
    Write-Host "  MONGO_URI=your_mongodb_connection_string" -ForegroundColor White
    Write-Host "  MISTRAL_API_KEY=your_mistral_api_key" -ForegroundColor White
    Write-Host "  OPENROUTER_API_KEY=your_openrouter_api_key" -ForegroundColor White
}

# Step 5: Success message
Write-Host ""
Write-Host "[5/5] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "     To start the application:" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal 1 - Start API Server:" -ForegroundColor Cyan
Write-Host "  uv run python run_server.py" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 - Start Streamlit Frontend:" -ForegroundColor Cyan
Write-Host "  uv run streamlit run frontend/app.py" -ForegroundColor White
Write-Host ""
Write-Host "Then open your browser:" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend: http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
