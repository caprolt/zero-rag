@echo off
echo 🚀 ZeroRAG Full Application Starter
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies if needed
if not exist "venv\Lib\site-packages\fastapi" (
    echo 📦 Installing Python dependencies...
    pip install -r requirements.txt
)

REM Start the full application
echo 🚀 Starting ZeroRAG...
python start_full_app.py

pause
