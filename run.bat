@echo off
REM =========================================
REM Transfermarkt Analytics Pro - Windows
REM =========================================
REM This script automatically:
REM   1. Checks Python installation
REM   2. Creates virtual environment
REM   3. Installs dependencies
REM   4. Launches the Streamlit app

setlocal enabledelayedexpansion
cd /d "%~dp0"

cls
echo.
echo =========================================
echo   Transfermarkt Analytics Pro v2.0
echo   Windows Startup Script
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.9+ from:
    echo   https://www.python.org/
    echo.
    echo During installation, make sure to check:
    echo   "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python !PYTHON_VERSION! found
echo.

REM Check if virtual environment exists
if exist "venv" (
    echo [OK] Virtual environment found
    echo [1/2] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [SETUP] Creating virtual environment...
    echo [1/3] Creating venv folder...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to create virtual environment
        echo Please check:
        echo   - Python is installed correctly
        echo   - You have write permissions in this folder
        echo   - Enough disk space is available
        echo.
        pause
        exit /b 1
    )
    
    echo [2/3] Activating virtual environment...
    call venv\Scripts\activate.bat
    
    echo [3/3] Installing dependencies (this may take 2-3 minutes)...
    pip install --upgrade pip setuptools wheel >nul 2>&1
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install dependencies
        echo Please check:
        echo   - Internet connection is working
        echo   - You have write permissions
        echo   - requirements.txt exists in this folder
        echo.
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed successfully
)

echo.
echo =========================================
echo   Starting Application
echo =========================================
echo.
echo [INFO] Opening at: http://localhost:8501
echo [INFO] Press Ctrl+C to stop the server
echo [INFO] First load may take 30 seconds...
echo.

REM Check if port 8501 is in use
netstat -ano | find ":8501" >nul 2>&1
if !errorlevel! equ 0 (
    echo [WARNING] Port 8501 is already in use!
    echo [INFO] Trying port 8502 instead...
    streamlit run app.py --server.port 8502
) else (
    streamlit run app.py
)

REM Keep window open if app crashes
echo.
echo [INFO] Application closed
pause
exit /b 0
