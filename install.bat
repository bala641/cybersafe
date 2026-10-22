@echo off
setlocal enabledelayedexpansion

echo.
echo =====================================================================
echo           CYBERSAFE NETWORK MONITOR - INSTALLER v2.1
echo =====================================================================
echo.

REM ── Admin check ──────────────────────────────────────────────────────────
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Please right-click install.bat and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)
echo [OK] Running as Administrator
echo.

REM ── Step 1: Check Python ─────────────────────────────────────────────────
echo [STEP 1/5] Checking Python...

python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo  Please install Python 3.9+ from: https://www.python.org/downloads/
    echo  IMPORTANT: Check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo [OK] !PY_VER! found
echo.

REM ── Step 2: Upgrade pip (with timeout + retries) ─────────────────────────
echo [STEP 2/5] Upgrading pip...

python -m pip install --upgrade pip ^
    --timeout 60 ^
    --retries 3 ^
    --quiet ^
    --disable-pip-version-check
echo [OK] pip upgraded
echo.

REM ── Step 3: Install dependencies ─────────────────────────────────────────
echo [STEP 3/5] Installing dependencies...
echo [INFO] This may take 3-8 minutes depending on your internet speed.
echo.

REM Install in batches so one failure doesn't kill everything

echo [*] Installing GUI packages...
python -m pip install ^
    "customtkinter>=5.2.2" ^
    "pillow>=10.4.0" ^
    "matplotlib>=3.9.0" ^
    "numpy>=2.0.0" ^
    --timeout 120 --retries 5 --prefer-binary --quiet
if %errorLevel% neq 0 (
    echo [WARN] Some GUI packages failed - retrying with --only-binary...
    python -m pip install ^
        "customtkinter>=5.2.2" ^
        "pillow>=10.4.0" ^
        "matplotlib>=3.9.0" ^
        "numpy>=2.0.0" ^
        --timeout 120 --retries 5 --only-binary=:all: --quiet
)

echo [*] Installing network packages...
python -m pip install ^
    "scapy>=2.5.0" ^
    "psutil>=5.9.6" ^
    --timeout 120 --retries 5 --prefer-binary --quiet

echo [*] Installing web packages...
python -m pip install ^
    "flask>=3.0.0" ^
    "flask-socketio>=5.3.5" ^
    "flask-cors>=4.0.0" ^
    "python-socketio>=5.10.0" ^
    --timeout 120 --retries 5 --prefer-binary --quiet

echo [*] Installing remaining packages...
python -m pip install ^
    "sqlalchemy>=2.0.23" ^
    "reportlab>=4.0.9" ^
    "python-docx>=0.8.11" ^
    "requests>=2.31.0" ^
    "colorama>=0.4.6" ^
    "pyyaml>=6.0.1" ^
    "pytz>=2023.3" ^
    "python-dateutil>=2.8.2" ^
    --timeout 120 --retries 5 --prefer-binary --quiet

echo [OK] Dependencies installed
echo.

REM ── Step 4: Create directories ───────────────────────────────────────────
echo [STEP 4/5] Setting up directories...
if not exist "%~dp0logs"           mkdir "%~dp0logs"
if not exist "%~dp0exports"        mkdir "%~dp0exports"
if not exist "%~dp0data"           mkdir "%~dp0data"
if not exist "%~dp0network_reports" mkdir "%~dp0network_reports"
echo [OK] Directories created
echo.

REM ── Step 5: Desktop shortcut with logo ───────────────────────────────────
echo [STEP 5/5] Creating desktop shortcut...

set ICON_PATH=%~dp0assets\cybersafe_logo.ico
if not exist "%ICON_PATH%" set ICON_PATH=%SystemRoot%\System32\SHELL32.dll,48

set VBS=%TEMP%\cs_shortcut.vbs
(
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo sLink = oWS.ExpandEnvironmentStrings^("%%USERPROFILE%%\Desktop\CyberSafe Network Monitor.lnk"^)
    echo Set oLink = oWS.CreateShortcut^(sLink^)
    echo oLink.TargetPath = "%~dp0START.bat"
    echo oLink.WorkingDirectory = "%~dp0"
    echo oLink.Description = "CyberSafe Network Traffic Monitoring"
    echo oLink.IconLocation = "%ICON_PATH%"
    echo oLink.Save
) > "%VBS%"
cscript //nologo "%VBS%"
del "%VBS%"

echo [OK] Desktop shortcut created with CyberSafe icon
echo.

REM ── Cleanup pycache ──────────────────────────────────────────────────────
for /d /r "%~dp0" %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d" 2>nul
)

REM ── Done ─────────────────────────────────────────────────────────────────
echo =====================================================================
echo                    INSTALLATION COMPLETE!
echo =====================================================================
echo.
echo  Launch: Double-click "CyberSafe Network Monitor" on your Desktop
echo          or double-click START.bat in this folder
echo.
echo =====================================================================
echo.

echo [*] Starting CyberSafe...
start "" "%~dp0START.bat"

timeout /t 3 >nul
exit /b 0
