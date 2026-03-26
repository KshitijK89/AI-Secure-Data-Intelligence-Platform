@echo off
echo 🛡️  AI Secure Data Intelligence Platform
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.10 or higher.
    exit /b 1
)

echo ✅ Python found
python --version

REM Backend Setup
echo.
echo 📦 Setting up Backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing backend dependencies...
pip install -r requirements.txt

echo.
echo ✅ Backend setup complete!
echo.

REM Frontend Setup
echo 📦 Setting up Frontend...
cd ..\frontend

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16 or higher.
    exit /b 1
)

echo ✅ Node.js found
node --version
echo ✅ npm found
npm --version

REM Install dependencies
echo Installing frontend dependencies...
call npm install

echo.
echo ✅ Frontend setup complete!
echo.
echo ========================================
echo 🎉 Setup Complete!
echo.
echo To start the application:
echo 1. Backend:  cd backend ^&^& python -m uvicorn app.main:app --reload
echo 2. Frontend: cd frontend ^&^& npm start
echo.
echo Or use start-backend.bat and start-frontend.bat
echo ========================================

pause
