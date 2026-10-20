@echo off
REM ============================================================================
REM CyberSafe Network Monitor - Automated One-Click Installer
REM ============================================================================

echo.
echo =====================================================================
echo           CYBERSAFE NETWORK MONITOR - INSTALLER v2.0
echo                   One-Click Installation System
echo =====================================================================
echo.

REM Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This installer requires Administrator privileges!
    echo Please right-click install.bat and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Running with Administrator privileges
echo.

REM ============================================================================
REM STEP 1: Check if Python is installed
REM ============================================================================
echo [STEP 1/5] Checking Python installation...

python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Python not found on this system
    echo [INFO] Checking if Python installer is bundled...
    
    if exist "%~dp0python-installer.exe" (
        echo [INFO] Found bundled Python installer
        echo [INFO] Installing Python... This may take a few minutes...
        "%~dp0python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
        echo [OK] Python installed successfully
    ) else (
        echo.
        echo [ERROR] Python is required but not installed!
        echo.
        echo Please download and install Python from:
        echo https://www.python.org/downloads/
        echo.
        echo Make sure to check "Add Python to PATH" during installation
        echo.
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [OK] !PYTHON_VERSION! detected
)

echo.

REM ============================================================================
REM STEP 2: Install Python dependencies
REM ============================================================================
echo [STEP 2/5] Installing required packages...
echo [INFO] This may take 2-5 minutes on first install...
echo.

REM Upgrade pip first
echo [*] Upgrading pip...
python -m pip install --upgrade pip --quiet --disable-pip-version-check

REM Install requirements
echo [*] Installing dependencies from requirements.txt...
echo     - Flask (Web Framework)
echo     - Scapy (Packet Capture)
echo     - CustomTkinter (GUI)
echo     - Matplotlib (Charts)
echo     - And more...
echo.

python -m pip install -r "%~dp0requirements.txt" --quiet --disable-pip-version-check

if %errorLevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo [OK] All dependencies installed successfully
echo.

REM ============================================================================
REM STEP 3: Create required directories
REM ============================================================================
echo [STEP 3/5] Setting up application directories...

if not exist "%~dp0logs" mkdir "%~dp0logs"
if not exist "%~dp0exports" mkdir "%~dp0exports"
if not exist "%~dp0data" mkdir "%~dp0data"
if not exist "%~dp0network_reports" mkdir "%~dp0network_reports"

echo [OK] Application directories created
echo.

REM ============================================================================
REM STEP 4: Create desktop shortcut
REM ============================================================================
echo [STEP 4/5] Creating desktop shortcut...

REM Create VBScript to generate shortcut
set SCRIPT="%TEMP%\create_shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = oWS.ExpandEnvironmentStrings("%%USERPROFILE%%\Desktop\CyberSafe Network Monitor.lnk") >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0START.bat" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "CyberSafe Network Traffic Monitoring and Threat Detection" >> %SCRIPT%
echo oLink.IconLocation = "%~dp0assets\cybersafe_logo.ico" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript //nologo %SCRIPT%
del %SCRIPT%

echo [OK] Desktop shortcut created
echo.

REM ============================================================================
REM STEP 5: Clean up cache files
REM ============================================================================
echo [STEP 5/5] Cleaning up temporary files...

if exist "%~dp0src\gui\__pycache__" rmdir /s /q "%~dp0src\gui\__pycache__"
if exist "%~dp0src\core\__pycache__" rmdir /s /q "%~dp0src\core\__pycache__"
if exist "%~dp0src\database\__pycache__" rmdir /s /q "%~dp0src\database\__pycache__"
if exist "%~dp0src\utils\__pycache__" rmdir /s /q "%~dp0src\utils\__pycache__"

echo [OK] Cleanup complete
echo.

REM ============================================================================
REM Installation Complete
REM ============================================================================
echo =====================================================================
echo                   INSTALLATION SUCCESSFUL!
echo =====================================================================
echo.
echo  CyberSafe Network Monitor is ready to use!
echo.
echo  What was installed:
echo  - Python runtime environment
echo  - Network monitoring engine
echo  - Threat detection system
echo  - Desktop GUI application
echo  - Report generation tools
echo.
echo  Launch options:
echo  1. Double-click "CyberSafe Network Monitor" on your desktop
echo  2. Double-click START.bat in this folder
echo  3. Run: python src/main.py --gui
echo.
echo =====================================================================
echo.

echo [*] Launching CyberSafe Network Monitor...
echo.

REM Launch the application
start "" "%~dp0START.bat"

echo [OK] Application is starting...
echo [OK] A new window should appear shortly
echo.
echo Installation complete! You can close this window.
echo.

timeout /t 5
exit /b 0
