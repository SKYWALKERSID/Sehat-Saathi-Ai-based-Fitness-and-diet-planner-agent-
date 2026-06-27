@echo off
cd /d "%~dp0"
title Sehat Saathi

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment (.venv) not found.
    echo Please ensure the virtual environment is set up properly.
    pause
    exit /b 1
)

echo Stopping any conflicting python server processes...
powershell -NoProfile -Command "Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*\.venv\Scripts\python.exe' } | Stop-Process -Force" >nul 2>nul

echo Starting Sehat Saathi server...
echo ----------------------------------------------------
echo Server logs will appear below. Keep this window open.
echo ----------------------------------------------------
echo.

:: Launch the browser in 3 seconds in the background
start "" cmd /c "timeout /t 3 >nul && start http://127.0.0.1:5000"

:: Run the server in the foreground
".venv\Scripts\python.exe" run.py

if errorlevel 1 (
    echo.
    echo [ERROR] Server exited with an error code.
    pause
)
