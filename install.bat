@echo off
REM ============================================================================
REM CyberSafe Network Monitor - One-Click Installer (Batch Wrapper)
REM This wrapper calls the PowerShell installer for better reliability
REM ============================================================================

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Run PowerShell with the installer script
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%INSTALL.ps1"

exit /b %errorlevel%
