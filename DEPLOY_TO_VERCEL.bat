@echo off
REM ======================================================================
REM CyberSafe Website Deployment to Vercel
REM This script pushes your website to GitHub and deploys to Vercel
REM ======================================================================

setlocal enabledelayedexpansion
cls

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║     CYBERSAFE WEBSITE DEPLOYMENT TO VERCEL                       ║
echo ║     This will push your website live!                            ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM Check if GitHub Desktop is installed
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in PATH
    echo Please download GitHub Desktop from: https://desktop.github.com
    pause
    exit /b 1
)

echo [OK] Git found!
echo.

REM Navigate to website directory
cd /d "c:\Users\admin\Downloads\Cyber safe\cybersafe.site"

if %errorlevel% neq 0 (
    echo [ERROR] Could not navigate to cybersafe.site directory
    pause
    exit /b 1
)

echo [OK] In cybersafe.site directory
echo.

REM Check if git repo exists
if not exist ".git" (
    echo [*] Git repository not found - initializing...
    git init
    git config user.name "CyberSafe Admin"
    git config user.email "admin@cybersafe.local"
)

echo [*] Adding files to git...
git add .

echo [*] Committing changes...
set COMMIT_MSG=CyberSafe website deployment - frontend ready for Vercel
git commit -m "%COMMIT_MSG%"

if %errorlevel% neq 0 (
    echo [WARNING] No changes to commit (files may already be committed)
)

echo [*] Checking git status...
git status

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║     NEXT STEPS:                                                   ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo 1. Go to: https://github.com/new
echo    - Repository name: cybersafe-website
echo    - Make it PUBLIC
echo    - Click Create Repository
echo.
echo 2. Copy your repository URL (looks like):
echo    https://github.com/YOUR-USERNAME/cybersafe-website.git
echo.
echo 3. Add remote and push (run these commands):
echo.
echo    git remote add origin [PASTE YOUR REPO URL HERE]
echo    git branch -M main
echo    git push -u origin main
echo.
echo 4. Go to: https://vercel.com
echo    - Click "Import Project"
echo    - Paste your repository URL
echo    - Set Root Directory to: ./frontend
echo    - Click Deploy
echo.
echo 5. Wait for deployment to complete (takes 3-5 minutes)
echo    - You'll get a live URL when done!
echo.
echo ═══════════════════════════════════════════════════════════════════
echo Files are ready! Follow steps 1-5 above to go live!
echo ═══════════════════════════════════════════════════════════════════
echo.

pause
