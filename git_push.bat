@echo off
cd /d "%~dp0"
echo Pushing to GitHub...
git push origin main
echo.
echo Push complete!
pause
