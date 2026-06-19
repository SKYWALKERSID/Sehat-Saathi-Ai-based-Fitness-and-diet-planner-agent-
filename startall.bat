@echo off
setlocal EnableExtensions

cd /d "%~dp0"
title Sehat Saathi

set "APP_VERSION=20260619-9"
set "APP_URL=http://127.0.0.1:5000/?v=%APP_VERSION%"
set "PYTHON_CMD=C:\Users\siddh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "VENV_DIR=%CD%\.venv"

if not exist "%PYTHON_CMD%" (
    set "PYTHON_CMD="
    where py >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON_CMD=py -3"
    ) else (
        where python >nul 2>nul
        if %errorlevel%==0 (
            set "PYTHON_CMD=python"
        )
    )
)

if not defined PYTHON_CMD (
    echo Python was not found on this machine.
    echo Install Python 3 or add it to PATH, then run this file again.
    pause
    exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating local virtual environment...
    "%PYTHON_CMD%" -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo.
        echo Failed to create the virtual environment.
        pause
        exit /b 1
    )

    echo Installing project dependencies...
    "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
    if errorlevel 1 (
        echo.
        echo Failed to upgrade pip.
        pause
        exit /b 1
    )

    "%VENV_DIR%\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Dependency installation failed.
        pause
        exit /b 1
    )

    echo Setup complete.
    echo.
) else (
    echo Existing virtual environment found. Skipping dependency installation.
    echo.
)

set "PYTHON_CMD=%VENV_DIR%\Scripts\python.exe"

echo Stopping any existing Sehat Saathi server instances...
powershell -NoProfile -Command "Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq '%VENV_DIR%\Scripts\python.exe' } | Stop-Process -Force" >nul 2>nul

echo Starting Sehat Saathi from:
echo %CD%
echo.
echo Using: %PYTHON_CMD%
echo.

start "Sehat Saathi Server" /min "%PYTHON_CMD%" run.py

echo Waiting for the local server to become ready...
for /l %%i in (1,1,45) do (
    powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:5000/' -UseBasicParsing -TimeoutSec 2).StatusCode | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
    if not errorlevel 1 goto :open_browser
    timeout /t 1 /nobreak >nul
)

echo.
echo Server did not respond in time.
echo Check the server window for errors.
pause
exit /b 1

:open_browser
echo Server is ready. Opening the dashboard...
start "" "%APP_URL%"
echo.
echo The browser should now show the latest dashboard layout.
exit /b 0

