import zipfile, os

BASE = r"C:\Users\admin\Downloads\Cyber safe"
DEST = r"C:\Users\admin\Downloads\Cyber safe\cybersafe.site\CyberSafe-Installer.zip"

root_files = [
    ("install.bat",            "install.bat"),
    ("START.bat",              "START.bat"),
    ("requirements.txt",       "requirements.txt"),
    ("README.md",              "README.md"),
    ("main.py",                "src/main.py"),
    ("dist_exe/CyberSafe.exe", "CyberSafe.exe"),  # real EXE with icon + name
]
src_dirs = [
    ("assets",   "assets"),
    ("gui",      "src/gui"),
    ("database", "src/database"),
    ("utils",    "src/utils"),
]
core_files = [
    "packet_capture.py", "port_monitor.py", "protocol_analyzer.py",
    "threat_detector.py", "user_tracker.py",
]

with zipfile.ZipFile(DEST, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:

    for src_rel, arc in root_files:
        fp = os.path.join(BASE, src_rel)
        if os.path.exists(fp):
            zf.write(fp, arc)
            print(f"  + {arc}  ({os.path.getsize(fp)//1024} KB)")
        else:
            print(f"  MISSING: {src_rel}")

    for dir_rel, prefix in src_dirs:
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
                arc = prefix + "/" + os.path.relpath(fp, dir_abs).replace(os.sep, "/")
                zf.write(fp, arc)
                print(f"  + {arc}")

    for f in core_files:
        fp = os.path.join(BASE, "core", f)
        if os.path.exists(fp):
            zf.write(fp, "src/core/" + f)
            print(f"  + src/core/{f}")

size_mb = os.path.getsize(DEST) / 1024 / 1024
print(f"\nZIP ready: {DEST}")
print(f"Total size: {size_mb:.1f} MB")
