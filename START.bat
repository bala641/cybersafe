@echo off
REM CyberSafe - Quick Launch (Hidden Console)
REM Launches CyberSafe GUI without visible console window

cd /d "%~dp0"

REM Run Python in background using pythonw (no console)
start /B pythonw main.py --gui

REM Alternative: Use VBS launcher for completely hidden launch
REM wscript launcher.vbs

