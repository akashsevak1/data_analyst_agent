@echo off
REM ============================================
REM  Data Analyst Agent - Windows launcher
REM  Double-click this file to start the app
REM ============================================

title Data Analyst Agent

echo ============================================
echo   Data Analyst Agent - Starting...
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python from https://python.org
    echo IMPORTANT: Check "Add Python to PATH" during install!
    echo.
    pause
    exit /b 1
)

echo [1/3] Python found.
echo.

REM Install dependencies if needed
echo [2/3] Checking/installing required libraries...
python -m pip install -r requirements.txt --quiet
echo Done.
echo.

REM Run the app
echo [3/3] Launching Data Analyst Agent...
echo Your browser will open automatically at http://localhost:8501
echo.
echo To STOP the app, close this window or press Ctrl+C
echo ============================================
echo.

python -m streamlit run app.py

pause
