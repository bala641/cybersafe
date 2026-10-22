"""
finalize_logo.py
- Converts the CS logo PNG to a proper multi-size .ico
- Copies it to assets/ and cybersafe.site/
- Rebuilds the installer ZIP (assets folder included)
"""
from PIL import Image
import zipfile, os, shutil

BASE  = r"C:\Users\admin\Downloads\Cyber safe"
LOGO_SRC = r"C:\Users\admin\Downloads\Black and White Simple Studio Logo (1).png"

ICO_DEST  = os.path.join(BASE, "assets", "cybersafe_logo.ico")
PNG_DEST  = os.path.join(BASE, "assets", "cybersafe_logo.png")
SITE_LOGO = os.path.join(BASE, "cybersafe.site", "logo.png")
SITE_FAV  = os.path.join(BASE, "cybersafe.site", "favicon.ico")
ZIP_DEST  = os.path.join(BASE, "cybersafe.site", "CyberSafe-Installer.zip")

# ── 1. Convert logo to proper ICO ──────────────────────────────────────────
print("1. Converting logo PNG → ICO ...")
img = Image.open(LOGO_SRC).convert("RGBA")
img.save(PNG_DEST)
img.save(ICO_DEST, format="ICO",
         sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
print(f"   ICO: {os.path.getsize(ICO_DEST):,} bytes")

# ── 2. Copy to website folder ───────────────────────────────────────────────
print("2. Copying logo to website folder ...")
shutil.copy2(PNG_DEST, SITE_LOGO)
shutil.copy2(ICO_DEST, SITE_FAV)
print(f"   logo.png  → {SITE_LOGO}")
print(f"   favicon.ico → {SITE_FAV}")

# ── 3. Rebuild installer ZIP ────────────────────────────────────────────────
print("3. Rebuilding installer ZIP ...")
root_files = [
    ("install.bat",      "install.bat"),
    ("START.bat",        "START.bat"),
    ("requirements.txt", "requirements.txt"),
    ("README.md",        "README.md"),
    ("main.py",          "src/main.py"),
]
src_dirs = [
    ("assets",   "assets"),          # ← logo/ico included here
    ("gui",      "src/gui"),
    ("database", "src/database"),
    ("utils",    "src/utils"),
]
core_files = [
    "packet_capture.py", "port_monitor.py", "protocol_analyzer.py",
    "threat_detector.py", "user_tracker.py",
]

with zipfile.ZipFile(ZIP_DEST, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for src_rel, arc in root_files:
        fp = os.path.join(BASE, src_rel)
        if os.path.exists(fp):
            zf.write(fp, arc); print(f"   + {arc}")

    for dir_rel, arc_prefix in src_dirs:
        dir_abs = os.path.join(BASE, dir_rel)
        if not os.path.isdir(dir_abs):
            continue
        for root, _, files in os.walk(dir_abs):
            if "__pycache__" in root:
                continue
            for f in files:
                if f.endswith(".pyc"):
                    continue
                fp  = os.path.join(root, f)
                arc = arc_prefix + "/" + os.path.relpath(fp, dir_abs).replace(os.sep, "/")
                zf.write(fp, arc); print(f"   + {arc}")

    for f in core_files:
        fp = os.path.join(BASE, "core", f)
        if os.path.exists(fp):
            zf.write(fp, "src/core/" + f); print(f"   + src/core/{f}")

size = os.path.getsize(ZIP_DEST) / 1024 / 1024
print(f"\n   ZIP ready: {ZIP_DEST}")
print(f"   Size: {size:.2f} MB")
print("\nDone!")
