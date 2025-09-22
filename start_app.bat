@echo off
echo 🤖 Starting ZeroRAG Application with Ollama restart...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found. Please run setup_dev.ps1 first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if required packages are installed
echo 🔍 Checking Python dependencies...
python -c "import requests, streamlit, uvicorn" 2>nul
if errorlevel 1 (
    echo ⚠️  Some required packages may be missing. Installing...
    pip install -r requirements.txt
)

REM Start the application with Ollama restart
echo 🚀 Starting ZeroRAG with Ollama restart...
python start_app.py

pause
