@echo off
REM CyberSafe - Quick Launch (Hidden Console)
REM Launches CyberSafe GUI without visible console window

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python not found! Please run install.bat first.
    pause
    exit /b 1
)

REM Run Python in background using pythonw (no console)
start /B pythonw "%~dp0src\main.py" --gui

REM Exit immediately
exit

