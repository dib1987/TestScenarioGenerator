@echo off
echo ======================================================================
echo PR Test Scenario Generator - Web Application
echo ======================================================================
echo.
echo Starting web server...
echo.
echo Once started, open your browser and go to:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ======================================================================
echo.

cd /d "%~dp0"

if not exist venv\Scripts\python.exe (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

venv\Scripts\python.exe app.py

if errorlevel 1 (
    echo.
    echo ERROR: Server exited with an error. See above for details.
)

pause
