@echo off
echo ======================================================================
echo PR Test Scenario Generator
echo ======================================================================
echo.
echo Starting application...
echo.
echo This is an interactive CLI tool that will guide you through
echo generating test scenarios from PR code changes.
echo.
echo Press Ctrl+C to exit
echo ======================================================================
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
python main.py

