@echo off
REM Resume Analyzer RAG - Quick Start Script
REM This script sets up and runs the application with UV

setlocal enabledelayedexpansion

echo.
echo ========================================================
echo     Resume Analyzer RAG - Quick Start
echo ========================================================
echo.

REM Check if UV is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] UV is not installed!
    echo.
    echo Please install UV first:
    echo   pipx install uv
    echo   OR
    echo   pip install uv
    echo.
    exit /b 1
)

echo [1/5] Creating virtual environment...
uv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    exit /b 1
)
echo [OK] Virtual environment created

echo.
echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat
echo [OK] Virtual environment activated

echo.
echo [3/5] Installing dependencies...
uv sync
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)
echo [OK] Dependencies installed

echo.
echo [4/5] Running connectivity tests...
uv run python test_connections.py
if errorlevel 1 (
    echo [WARNING] Some tests failed - check .env file
    echo.
    echo Please ensure you have created a .env file with:
    echo   MONGO_URI=your_mongodb_connection_string
    echo   MISTRAL_API_KEY=your_mistral_api_key
    echo   OPENROUTER_API_KEY=your_openrouter_api_key
)

echo.
echo [5/5] Setup complete!
echo.
echo ========================================================
echo     To start the application:
echo ========================================================
echo.
echo Terminal 1 - Start API Server:
echo   uv run python run_server.py
echo.
echo Terminal 2 - Start Streamlit Frontend:
echo   uv run streamlit run frontend/app.py
echo.
echo Then open your browser:
echo   API Docs: http://localhost:8000/docs
echo   Frontend: http://localhost:8501
echo.
echo ========================================================
echo.

pause
