@echo off
REM CyberSafe - Quick Launch (Hidden)
REM Launches CyberSafe with no visible console window

cd /d "%~dp0"

REM Use VBS to run Python completely hidden
cscript.exe "%~dp0launcher.vbs"
exit /b 0
