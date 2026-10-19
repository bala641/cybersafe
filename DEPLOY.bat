@echo off
REM ============================================================================
REM CyberSafe Deployment Script
REM Run this script to push changes to GitHub and trigger Vercel deployment
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo.
echo         CyberSafe - GitHub Push & Vercel Deployment
echo                      Automated Deployment
echo.
echo ====================================================================
echo.

REM ============================================================================
REM Step 1: Verify Git Installation
REM ============================================================================

echo [STEP 1/4] Checking Git installation...
git --version >nul 2>&1

if %errorlevel% neq 0 (
    echo [ERROR] Git not found. Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

echo [OK] Git is installed
echo.

REM ============================================================================
REM Step 2: Configure Git (if needed)
REM ============================================================================

echo [STEP 2/4] Configuring Git...

git config --global credential.helper manager >nul 2>&1

echo [OK] Git configured for Windows credential manager
echo.

REM ============================================================================
REM Step 3: Stage and Commit Changes
REM ============================================================================

echo [STEP 3/4] Preparing changes for push...
echo.

cd /d "%~dp0"

REM Show status
echo Current Git Status:
echo ─────────────────────────────────────
git status

echo.
echo [*] Staging all changes...
git add -A

echo.
echo [*] Creating commit...
git commit -m "CyberSafe Update: Wireshark UI, separated graphs, export system, automated deployment" 2>nul

if %errorlevel% neq 0 (
    echo [WARNING] No changes to commit (or commit failed)
    echo If you want to force a deployment, run: git commit --allow-empty -m "Trigger deployment"
) else (
    echo [OK] Changes committed successfully
)

echo.

REM ============================================================================
REM Step 4: Push to GitHub
REM ============================================================================

echo [STEP 4/4] Pushing to GitHub...
echo.
echo [*] Connecting to https://github.com/bala641/cybersafe...
echo [*] Enter your GitHub credentials when prompted
echo.

git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ====================================================================
    echo                    PUSH SUCCESSFUL!
    echo ====================================================================
    echo.
    echo Changes have been pushed to GitHub!
    echo.
    echo NEXT STEPS:
    echo 1. Go to: https://vercel.com/dashboard/bala17
    echo 2. Select "cybersafe" project
    echo 3. New deployment should start automatically
    echo 4. Wait for "Ready" status (usually 2-5 minutes)
    echo 5. Visit your live site at: https://cybersafe.vercel.app
    echo.
    echo You can track deployment at:
    echo https://vercel.com/bala17/cybersafe/deployments
    echo.
) else (
    echo.
    echo ====================================================================
    echo                     PUSH FAILED
    echo ====================================================================
    echo.
    echo [ERROR] Could not push to GitHub
    echo.
    echo TROUBLESHOOTING:
    echo 1. Check internet connection
    echo 2. Verify GitHub credentials are correct
    echo 3. Check repository is accessible: https://github.com/bala641/cybersafe
    echo 4. Try: git push -u origin main
    echo.
)

echo.
echo Press any key to exit...
pause

exit /b %errorlevel%
