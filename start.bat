@echo off
echo ========================================
echo Starting Organization Management System
echo ========================================
echo.

REM Check if .env exists, if not copy from .env.local
if not exist .env (
    echo Creating .env file...
    copy .env.local .env
    echo .env file created!
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API Docs will be at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
