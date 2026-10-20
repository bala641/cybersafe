Add-Type -AssemblyName System.Drawing

$basePath = "C:\Users\admin\Downloads\Cyber safe"
$pngPath  = "$basePath\assets\cybersafe_logo.png"
$icoPath  = "$basePath\assets\cybersafe_logo.ico"

$png = [System.Drawing.Image]::FromFile($pngPath)

function ResizeBmp($src, $size) {
    $bmp = New-Object System.Drawing.Bitmap($size, $size)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.SmoothingMode     = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.DrawImage($src, 0, 0, $size, $size)
    $g.Dispose()
    return $bmp
}

function BmpToBytes($bmp) {
    $ms = New-Object System.IO.MemoryStream
    $bmp.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
    $bytes = $ms.ToArray()
    $ms.Dispose()
    return $bytes
}

$sizes = @(16, 32, 48, 256)
$images = @{}
foreach ($s in $sizes) {
    $b = ResizeBmp $png $s
    $images[$s] = BmpToBytes $b
    $b.Dispose()
}
$png.Dispose()

# Write ICO file
$numImages  = $sizes.Count
$headerSize = 6
$dirSize    = 16 * $numImages
$dataOffset = $headerSize + $dirSize

$ms = New-Object System.IO.MemoryStream
$bw = New-Object System.IO.BinaryWriter($ms)

# ICO file header
$bw.Write([uint16]0)          # reserved
$bw.Write([uint16]1)          # image type: 1=ICO
$bw.Write([uint16]$numImages) # number of images

# Directory entries
$offset = [uint32]$dataOffset
foreach ($s in $sizes) {
    $bytes = $images[$s]
    $w = if ($s -eq 256) { 0 } else { [byte]$s }
    $h = if ($s -eq 256) { 0 } else { [byte]$s }
    $bw.Write([byte]$w)
    $bw.Write([byte]$h)
    $bw.Write([byte]0)          # color count
    $bw.Write([byte]0)          # reserved
    $bw.Write([uint16]1)        # color planes
    $bw.Write([uint16]32)       # bits per pixel
    $bw.Write([uint32]$bytes.Length)
    $bw.Write([uint32]$offset)
    $offset += [uint32]$bytes.Length
}

# Image data
foreach ($s in $sizes) {
    $bw.Write($images[$s])
}

$bw.Flush()
[System.IO.File]::WriteAllBytes($icoPath, $ms.ToArray())
$ms.Dispose()
$bw.Dispose()

$finalSize = (Get-Item $icoPath).Length
Write-Host "ICO created: $icoPath ($finalSize bytes)"
