@echo off
REM Create desktop shortcuts for easy launch

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Create VBS script for shortcut
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = oWS.SpecialFolders("Desktop"^) ^& "\CyberSafe.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "%CD%\START.bat"
    echo oLink.WorkingDirectory = "%CD%"
    echo oLink.Description = "CyberSafe Network Monitor"
    echo oLink.Save
    echo WScript.Echo "Shortcut created on Desktop!"
) > create_link.vbs

cscript create_link.vbs
del create_link.vbs

echo.
echo ========================================
echo Desktop shortcut created!
echo Double-click "CyberSafe" on your desktop
echo to launch the application
echo ========================================
pause
