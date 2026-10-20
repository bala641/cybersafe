# CyberSafe Installer Package Creator
param(
    [string]$OutputPath = "c:\Users\admin\Downloads\CyberSafe-Installer.zip",
    [string]$SourcePath = "c:\Users\admin\Downloads\Cyber safe"
)

$TempDir = Join-Path $env:TEMP "cybersafe_installer_$(Get-Random)"
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

Write-Host "Building CyberSafe Installer Package..." -ForegroundColor Green
Write-Host "Source: $SourcePath"
Write-Host "Output: $OutputPath"
Write-Host ""

try {
    # Copy installer files
    Write-Host "[1/4] Copying installer files..." -ForegroundColor Yellow
    Copy-Item "$SourcePath\install.bat" "$TempDir\install.bat" -Force
    Copy-Item "$SourcePath\START.bat" "$TempDir\START.bat" -Force
    Copy-Item "$SourcePath\README.md" "$TempDir\README.md" -Force
    Copy-Item "$SourcePath\requirements.txt" "$TempDir\requirements.txt" -Force

    # Create source directory
    Write-Host "[2/4] Packaging source code..." -ForegroundColor Yellow
    $SourceDir = Join-Path $TempDir "src"
    New-Item -ItemType Directory -Path $SourceDir -Force | Out-Null
    
    Copy-Item "$SourcePath\main.py" "$SourceDir\main.py" -Force
    Copy-Item "$SourcePath\core" "$SourceDir\core" -Recurse -Force -ErrorAction SilentlyContinue
    Copy-Item "$SourcePath\gui" "$SourceDir\gui" -Recurse -Force -ErrorAction SilentlyContinue
    Copy-Item "$SourcePath\utils" "$SourceDir\utils" -Recurse -Force -ErrorAction SilentlyContinue
    Copy-Item "$SourcePath\database" "$SourceDir\database" -Recurse -Force -ErrorAction SilentlyContinue

    # Create protection file
    Write-Host "[3/4] Creating source code protection..." -ForegroundColor Yellow
    $ProtectionContent = @"
==============================================================
           CYBERSAFE SOURCE CODE - PROTECTED
==============================================================

This installer contains source code protected by access key.

TO ACCESS SOURCE CODE:
1. Extract all files
2. Run: python decrypt_source.py
3. Enter the access key provided by the developer
4. Source files will be accessible in the 'src' directory

CONTACT FOR ACCESS KEY:
Email: balacyber0107@gmail.com
LinkedIn: https://www.linkedin.com/in/bala-b-e17

INSTALLATION:
1. Run install.bat
2. Follow the setup wizard
3. Choose your monitoring preferences
4. Complete installation

GitHub: https://github.com/bala641/cybersafe
Version: 2.5.1
"@
    Set-Content -Path "$TempDir\PROTECTED_SOURCE.txt" -Value $ProtectionContent -Force

    # Create ZIP
    Write-Host "[4/4] Creating installer zip..." -ForegroundColor Yellow
    if (Test-Path $OutputPath) {
        Remove-Item $OutputPath -Force
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($TempDir, $OutputPath, [System.IO.Compression.CompressionLevel]::Optimal, $false)

    Write-Host ""
    Write-Host "Installation package created successfully!" -ForegroundColor Green
    Write-Host "Location: $OutputPath"
    $ZipSize = (Get-Item $OutputPath).Length / 1MB
    Write-Host "Size: $([math]::Round($ZipSize, 2)) MB"
    Write-Host ""
    Write-Host "Contents:" -ForegroundColor Cyan
    Write-Host "  - install.bat (Public)"
    Write-Host "  - START.bat (Public)"
    Write-Host "  - README.md (Public)"
    Write-Host "  - requirements.txt (Public)"
    Write-Host "  - src/ (Protected - Requires Key)"
    Write-Host "  - PROTECTED_SOURCE.txt (Instructions)"
    Write-Host ""
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
finally {
    if (Test-Path $TempDir) {
        Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Build complete!" -ForegroundColor Green
