@echo off
echo 🤖 Starting ZeroRAG Application...
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

REM Start the application
echo 🚀 Starting ZeroRAG...
python start_app.py

pause
