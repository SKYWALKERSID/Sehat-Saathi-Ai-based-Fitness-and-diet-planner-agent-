@echo off
cd /d "%~dp0"
title Sehat Saathi

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment (.venv) not found.
    echo Please ensure the virtual environment is configured properly.
    pause
    exit /b 1
)

echo Starting Sehat Saathi local development server...
start "Sehat Saathi Server" ".venv\Scripts\python.exe" run.py

echo Waiting for server to spin up...
timeout /t 3 >nul

echo Opening browser at http://127.0.0.1:5000...
start "" "http://127.0.0.1:5000"
exit /b 0
