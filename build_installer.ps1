Add-Type -AssemblyName System.IO.Compression.FileSystem

$base = "C:\Users\admin\Downloads\Cyber safe"
$pkg  = "$base\installer_package"
$dest = "$base\cybersafe.site\CyberSafe-Installer.zip"

# Clean slate
if (Test-Path $pkg)  { Remove-Item $pkg  -Recurse -Force }
if (Test-Path $dest) { Remove-Item $dest -Force }

# Stage root files
New-Item -ItemType Directory -Path $pkg -Force | Out-Null
Copy-Item "$base\install.bat"      "$pkg\install.bat"
Copy-Item "$base\START.bat"        "$pkg\START.bat"
Copy-Item "$base\requirements.txt" "$pkg\requirements.txt"
Copy-Item "$base\README.md"        "$pkg\README.md"

# Stage assets/
Copy-Item "$base\assets" "$pkg\assets" -Recurse

# Stage src/
New-Item -ItemType Directory -Path "$pkg\src" -Force | Out-Null

if (Test-Path "$base\main.py") {
    Copy-Item "$base\main.py" "$pkg\src\main.py"
}

# gui, database, utils - copy whole folder then strip pycache
foreach ($d in @("gui","database","utils")) {
    if (Test-Path "$base\$d") {
        Copy-Item "$base\$d" "$pkg\src\$d" -Recurse
    }
}

# core - only .py files (avoid nested mess)
New-Item -ItemType Directory -Path "$pkg\src\core" -Force | Out-Null
Get-ChildItem "$base\core" -File -Filter "*.py" | ForEach-Object {
    Copy-Item $_.FullName "$pkg\src\core\$($_.Name)"
}

# Strip all __pycache__
Get-ChildItem $pkg -Recurse -Directory -Filter "__pycache__" |
    Remove-Item -Recurse -Force

# Print manifest
Write-Host "Package contents:"
Get-ChildItem $pkg -Recurse -File | ForEach-Object {
    Write-Host "  $($_.FullName.Replace($pkg,''))"
}

# Create ZIP
[System.IO.Compression.ZipFile]::CreateFromDirectory(
    $pkg, $dest,
    [System.IO.Compression.CompressionLevel]::Optimal,
    $false
)

$size = [math]::Round((Get-Item $dest).Length / 1MB, 2)
Write-Host "`nZIP created: $dest"
Write-Host "Size: $size MB"

# Cleanup
Remove-Item $pkg -Recurse -Force
Write-Host "Done."
