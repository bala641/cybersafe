"""
CyberSafe Network Monitor - Launcher
This file is compiled into CyberSafe.exe
"""
import sys
import os
import subprocess

def main():
    # Get directory where the EXE lives (works both frozen and unfrozen)
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to main app
    main_py = os.path.join(base_dir, "src", "main.py")
    if not os.path.exists(main_py):
        # fallback: check same dir
        main_py = os.path.join(base_dir, "main.py")

    if not os.path.exists(main_py):
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk(); root.withdraw()
        messagebox.showerror(
            "CyberSafe",
            f"Cannot find main.py\nExpected at: {main_py}\n\nPlease reinstall CyberSafe."
        )
        return

    # Launch with pythonw so no console window appears
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = "pythonw"

    subprocess.Popen(
        [pythonw, main_py, "--gui"],
        cwd=base_dir,
        creationflags=0x00000008  # DETACHED_PROCESS
    )

if __name__ == "__main__":
    main()
