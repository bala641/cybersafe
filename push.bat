@echo off
cd /d "%~dp0"
echo Pushing to GitHub...
git push origin main
echo.
echo Done! Check status above.
pause
