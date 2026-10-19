# CyberSafe Network Monitor - One-Click Installer (PowerShell Version)

Write-Host "`n"
Write-Host "====================================================================="
Write-Host "              CYBERSAFE NETWORK MONITOR - INSTALLER v1.0"
Write-Host "                    Professional One-Click Setup"
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "`n"

$ErrorActionPreference = "Stop"

# STEP 1: Check Python
Write-Host "[STEP 1/5] Checking Python installation..." -ForegroundColor Cyan

$python = (Get-Command python -ErrorAction SilentlyContinue)
if ($null -eq $python) {
    Write-Host "[ERROR] Python not found. Please install Python 3.11+ from python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

$version = python --version
Write-Host "[OK] Python is installed: $version" -ForegroundColor Green
Write-Host "`n"

# STEP 2: Install Dependencies
Write-Host "[STEP 2/5] Installing all required software packages..." -ForegroundColor Cyan
Write-Host "[*] This includes: Flask, Scapy, Matplotlib, NumPy, CustomTkinter, etc." 
Write-Host "[*] This may take 3-5 minutes on first install..."
Write-Host "`n"

Set-Location $PSScriptRoot

Write-Host "[*] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host "[*] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] All dependencies installed successfully" -ForegroundColor Green
Write-Host "`n"

# STEP 3: Clean Up
Write-Host "[STEP 3/5] Cleaning up unnecessary files..." -ForegroundColor Cyan

$dirs_to_remove = @("gui\__pycache__", "core\__pycache__", "utils\__pycache__", "__pycache__", "build", "dist")

foreach ($dir in $dirs_to_remove) {
    if (Test-Path $dir) {
        Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue
        Write-Host "[OK] Removed $dir" -ForegroundColor Green
    }
}

Write-Host "[OK] Cleanup complete" -ForegroundColor Green
Write-Host "`n"

# STEP 4: Create Desktop Shortcut
Write-Host "[STEP 4/5] Creating desktop shortcut..." -ForegroundColor Cyan

$desktop = [System.Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "CyberSafe Network Monitor.lnk"
$targetPath = Join-Path $PSScriptRoot "START.bat"
$iconPath = Join-Path $PSScriptRoot "assets\cybersafe_logo.ico"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.Description = "CyberSafe Network Traffic Monitoring and Threat Detection"
if (Test-Path $iconPath) {
    $shortcut.IconLocation = $iconPath
}
$shortcut.WindowStyle = 0
$shortcut.Save()

Write-Host "[OK] Desktop shortcut created with CyberSafe logo" -ForegroundColor Green
Write-Host "`n"

# STEP 5: Create Directories
Write-Host "[STEP 5/5] Setting up application directories..." -ForegroundColor Cyan

$dirs = @("logs", "exports", "network_reports", "data")

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force > $null
        Write-Host "[OK] Created $dir directory" -ForegroundColor Green
    }
}

Write-Host "`n"

# Installation Complete
Write-Host "====================================================================="
Write-Host "                    INSTALLATION SUCCESSFUL!" -ForegroundColor Green
Write-Host "`n"
Write-Host "  CyberSafe Network Monitor is ready to use!"
Write-Host "`n"
Write-Host "  What was installed:"
Write-Host "  - Python with all dependencies"
Write-Host "  - Network monitoring engine"
Write-Host "  - Web framework and Desktop GUI"
Write-Host "  - Graphics engine and Report generation"
Write-Host "  - Database layer"
Write-Host "`n"
Write-Host "  Launch options:"
Write-Host "  1. Double-click 'CyberSafe Network Monitor' on your desktop"
Write-Host "  2. Double-click START.bat"
Write-Host "  3. Run: python main.py --gui"
Write-Host "`n"
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "`n"

Write-Host "[*] Launching CyberSafe Network Monitor..." -ForegroundColor Yellow
Write-Host "`n"

# Launch the app
Start-Process -FilePath (Join-Path $PSScriptRoot "START.bat") -WorkingDirectory $PSScriptRoot

Write-Host "[OK] Application is starting..." -ForegroundColor Green
Write-Host "[OK] The application window should appear shortly" -ForegroundColor Green
Write-Host "`n"
Write-Host "Installation complete! Enjoy CyberSafe!" -ForegroundColor Green
Write-Host "`n"

Start-Sleep -Seconds 3
