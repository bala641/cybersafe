@echo off
REM Create desktop shortcut for hidden launch

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Create VBS script for shortcut that launches with NO CONSOLE
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = oWS.SpecialFolders("Desktop"^) ^& "\CyberSafe.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "%CD%\launcher.vbs"
    echo oLink.WorkingDirectory = "%CD%"
    echo oLink.Description = "CyberSafe Network Monitor - No Console"
    echo oLink.IconLocation = "%CD%\assets\cybersafe_logo.ico"
    echo oLink.Save
    echo WScript.Echo "Shortcut created on Desktop!"
) > create_link.vbs

cscript //nologo create_link.vbs
del create_link.vbs

echo.
echo ========================================
echo Desktop shortcut created!
echo Double-click "CyberSafe" on your desktop
echo to launch - NO CONSOLE WINDOW will appear
echo Only the GUI will be visible
echo ========================================
pause
