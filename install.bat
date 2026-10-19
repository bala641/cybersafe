@echo off
REM CyberSafe Network Monitor - Auto Installer
REM This script automatically installs Python, dependencies, and launches CyberSafe

setlocal enabledelayedexpansion
cls

echo.
echo ================================================
echo        CYBERSAFE NETWORK MONITOR
echo              Auto Installer v1.0
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python already installed
    python --version
    echo.
) else (
    echo [*] Python not found - Downloading and installing...
    echo.
    
    REM Download Python installer
    set PYTHON_INSTALLER=%TEMP%\python-installer.exe
    
    echo Downloading Python 3.11...
    powershell -NoProfile -Command ^
      "$ProgressPreference = 'SilentlyContinue'; ^
      Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' ^
      -OutFile '%PYTHON_INSTALLER%'" >nul 2>&1
    
    if not exist "%PYTHON_INSTALLER%" (
        echo [ERROR] Could not download Python
        echo Please download from: https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH"
        pause
        exit /b 1
    )
    
    echo [OK] Python downloaded
    echo [*] Installing Python...
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 >nul 2>&1
    
    if %errorlevel% neq 0 (
        echo [ERROR] Python installation failed
        pause
        exit /b 1
    )
    
    echo [OK] Python installed successfully
    echo.
)

REM Install dependencies
echo [*] Installing dependencies...
cd /d "%~dp0"

python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Create desktop shortcut for easy access
echo [*] Creating desktop shortcut...
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = oWS.SpecialFolders("Desktop"^) ^& "\CyberSafe.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "%CD%\START.bat"
    echo oLink.WorkingDirectory = "%CD%"
    echo oLink.Description = "CyberSafe Network Monitor"
    echo oLink.IconLocation = "%CD%\assets\cybersafe_logo.ico"
    echo oLink.WindowStyle = 0
    echo oLink.Save
) > "%TEMP%\create_link.vbs"

cscript "%TEMP%\create_link.vbs" >nul 2>&1
del "%TEMP%\create_link.vbs" >nul 2>&1

echo [OK] Shortcut created on desktop
echo.

REM Launch CyberSafe
echo ================================================
echo [OK] Installation complete!
echo.
echo Next time, just double-click the "CyberSafe"
echo shortcut on your desktop!
echo.
echo [*] Launching CyberSafe...
echo ================================================
echo.

if exist "main.py" (
    start "" python main.py --gui
    exit /b 0
) else (
    echo [ERROR] main.py not found
    pause
    exit /b 1
)
