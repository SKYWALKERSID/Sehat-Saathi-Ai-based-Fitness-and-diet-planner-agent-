@echo off
cd /d "%~dp0"
title Sehat Saathi

echo [1/3] Checking virtual environment...
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo [ERROR] Virtual environment (.venv) was not found in:
    echo %CD%\.venv
    echo.
    pause
    exit /b 1
)

echo [2/3] Launching browser in background...
start "" cmd /c "timeout /t 3 >nul && start http://127.0.0.1:5000"

echo [3/3] Starting Flask application...
echo --------------------------------------------------
".venv\Scripts\python.exe" run.py
echo --------------------------------------------------
echo.
echo Flask server has stopped running.
pause
