Add-Type -AssemblyName System.IO.Compression.FileSystem

$base = "C:\Users\admin\Downloads\Cyber safe"
$dest = "$base\cybersafe.site\CyberSafe-Installer.zip"

# Remove old ZIP
if (Test-Path $dest) { Remove-Item $dest -Force }

# Create new ZIP
$zip = [System.IO.Compression.ZipFile]::Open($dest, [System.IO.Compression.ZipArchiveMode]::Create)

function Add-FileToZip($zip, $filePath, $entryName) {
    $entry = $zip.CreateEntry($entryName, [System.IO.Compression.CompressionLevel]::Optimal)
    $stream = $entry.Open()
    $bytes  = [System.IO.File]::ReadAllBytes($filePath)
    $stream.Write($bytes, 0, $bytes.Length)
    $stream.Close()
}

function Add-DirToZip($zip, $dirPath, $zipPrefix) {
    Get-ChildItem $dirPath -Recurse -File | ForEach-Object {
        $rel   = $_.FullName.Substring($dirPath.Length).TrimStart('\').Replace('\','/')
        $entry = "$zipPrefix/$rel"
        Add-FileToZip $zip $_.FullName $entry
        Write-Host "  + $entry"
    }
}

# Root files
foreach ($f in @("install.bat","START.bat","requirements.txt","README.md")) {
    if (Test-Path "$base\$f") { Add-FileToZip $zip "$base\$f" $f ; Write-Host "  + $f" }
}

# assets/ folder
Add-DirToZip $zip "$base\assets" "assets"

# src/ — copy only clean source files
$srcDirs = @("gui","database","utils")
foreach ($d in $srcDirs) {
    if (Test-Path "$base\$d") { Add-DirToZip $zip "$base\$d" "src/$d" }
}

# core/ — only the .py files (not nested dirs that got copied by accident)
Get-ChildItem "$base\core" -File -Filter "*.py" | ForEach-Object {
    Add-FileToZip $zip $_.FullName "src/core/$($_.Name)"
    Write-Host "  + src/core/$($_.Name)"
}

# main.py
if (Test-Path "$base\main.py") {
    Add-FileToZip $zip "$base\main.py" "src/main.py"
    Write-Host "  + src/main.py"
}

$zip.Dispose()

$size = [math]::Round((Get-Item $dest).Length / 1MB, 2)
Write-Host "`nDone! ZIP: $dest ($size MB)"
