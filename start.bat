@echo off
echo 🏀 NBA Sports Betting Expert System
echo ================================
echo.
echo Starting the application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.7 or higher.
    echo Download from: https://www.python.org/downloads/
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

REM Install/update requirements
echo 📦 Installing/updating dependencies...
pip install -r requirements.txt

REM Start the application
echo.
echo 🚀 Starting NBA Betting Expert...
echo.
python start.py

echo.
echo 👋 Thanks for using NBA Betting Expert!
pause
