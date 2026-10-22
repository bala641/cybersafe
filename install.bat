@echo off
setlocal enabledelayedexpansion

echo.
echo =====================================================================
echo           CYBERSAFE NETWORK MONITOR - INSTALLER v2.2
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
echo [STEP 1/6] Checking Python...

python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed or not in PATH!
    echo  Please install Python 3.9+ from: https://www.python.org/downloads/
    echo  IMPORTANT: Check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo [OK] !PY_VER! found
echo.

REM ── Step 2: Upgrade pip ──────────────────────────────────────────────────
echo [STEP 2/6] Upgrading pip...
python -m pip install --upgrade pip --timeout 60 --retries 3 --quiet --disable-pip-version-check
echo [OK] pip ready
echo.

REM ── Step 3: Install dependencies ─────────────────────────────────────────
echo [STEP 3/6] Installing dependencies...
echo [INFO] This may take 3-8 minutes on first install.
echo.

echo [*] GUI packages (CustomTkinter, Pillow, Matplotlib)...
python -m pip install "customtkinter>=5.2.2" "pillow>=10.4.0" "matplotlib>=3.9.0" "numpy>=2.0.0" --timeout 120 --retries 5 --prefer-binary --quiet
if %errorLevel% neq 0 (
    python -m pip install "customtkinter>=5.2.2" "pillow>=10.4.0" "matplotlib>=3.9.0" "numpy>=2.0.0" --timeout 120 --retries 5 --only-binary=:all: --quiet
)

echo [*] Network packages (Scapy, psutil)...
python -m pip install "scapy>=2.5.0" "psutil>=5.9.6" --timeout 120 --retries 5 --prefer-binary --quiet

echo [*] Web packages (Flask)...
python -m pip install "flask>=3.0.0" "flask-socketio>=5.3.5" "flask-cors>=4.0.0" "python-socketio>=5.10.0" --timeout 120 --retries 5 --prefer-binary --quiet

echo [*] Remaining packages...
python -m pip install "sqlalchemy>=2.0.23" "reportlab>=4.0.9" "python-docx>=0.8.11" "requests>=2.31.0" "colorama>=0.4.6" "pyyaml>=6.0.1" "pytz>=2023.3" "python-dateutil>=2.8.2" --timeout 120 --retries 5 --prefer-binary --quiet

echo [OK] All dependencies installed
echo.

REM ── Step 4: Setup directories ────────────────────────────────────────────
echo [STEP 4/6] Setting up directories...
if not exist "%~dp0logs"            mkdir "%~dp0logs"
if not exist "%~dp0exports"         mkdir "%~dp0exports"
if not exist "%~dp0data"            mkdir "%~dp0data"
if not exist "%~dp0network_reports" mkdir "%~dp0network_reports"
echo [OK] Directories ready
echo.

REM ── Step 5: Register app in Windows (so it shows in Search as "CyberSafe") ──
echo [STEP 5/6] Registering CyberSafe in Windows...

set EXE_PATH=%~dp0CyberSafe.exe
set ICO_PATH=%~dp0assets\cybersafe_logo.ico

REM App Paths - this makes "CyberSafe" findable in Start Menu / Search
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\CyberSafe.exe" /ve /d "%EXE_PATH%" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\CyberSafe.exe" /v "Path" /d "%~dp0" /f >nul 2>&1

REM Add to Apps & Features list with proper name
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CyberSafeNetworkMonitor" /v "DisplayName"     /d "CyberSafe Network Monitor" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CyberSafeNetworkMonitor" /v "DisplayVersion"  /d "2.0.0"                     /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CyberSafeNetworkMonitor" /v "Publisher"       /d "Bala B"                    /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CyberSafeNetworkMonitor" /v "DisplayIcon"     /d "%ICO_PATH%"                /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CyberSafeNetworkMonitor" /v "InstallLocation" /d "%~dp0"                     /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CyberSafeNetworkMonitor" /v "UninstallString" /d "cmd /c del /f \"%EXE_PATH%\"" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CyberSafeNetworkMonitor" /v "NoModify"        /t REG_DWORD /d 1              /f >nul 2>&1

echo [OK] CyberSafe registered - will appear in Windows Search as "CyberSafe"
echo.

REM ── Step 6: Desktop shortcut pointing to CyberSafe.exe ───────────────────
echo [STEP 6/6] Creating desktop shortcut...

set VBS=%TEMP%\cs_shortcut.vbs
(
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo sLink = oWS.ExpandEnvironmentStrings^("%%USERPROFILE%%\Desktop\CyberSafe Network Monitor.lnk"^)
    echo Set oLink = oWS.CreateShortcut^(sLink^)
    echo oLink.TargetPath = "%EXE_PATH%"
    echo oLink.WorkingDirectory = "%~dp0"
    echo oLink.Description = "CyberSafe - Network Traffic Monitoring and Threat Detection"
    echo oLink.IconLocation = "%ICO_PATH%"
    echo oLink.Save
) > "%VBS%"
cscript //nologo "%VBS%"
del "%VBS%" >nul 2>&1
echo [OK] Desktop shortcut created
echo.

REM ── Cleanup ───────────────────────────────────────────────────────────────
for /d /r "%~dp0" %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d" 2>nul
)

REM ── Done ──────────────────────────────────────────────────────────────────
echo =====================================================================
echo                    INSTALLATION COMPLETE!
echo =====================================================================
echo.
echo  Search "CyberSafe" in Windows Start Menu to launch
echo  OR double-click "CyberSafe Network Monitor" on your Desktop
echo  OR double-click CyberSafe.exe in this folder
echo.
echo =====================================================================
echo.

echo [*] Launching CyberSafe...
start "" "%EXE_PATH%"

timeout /t 3 >nul
exit /b 0
