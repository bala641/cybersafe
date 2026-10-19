@echo off
REM CyberSafe - Hidden Console Launcher
REM This launcher ensures NO console window appears

cd /d "%~dp0"

REM Use VBS script to launch completely hidden
wscript //B launcher.vbs

REM Exit immediately (no window flash)
exit
