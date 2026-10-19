#!/usr/bin/env python3
"""Test GUI startup"""

import sys
import os
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Importing customtkinter...")
    import customtkinter as ctk
    print("✓ customtkinter imported")
    
    print("Importing desktop_app...")
    from gui.desktop_app import CyberSafeGUI
    print("✓ desktop_app imported")
    
    print("Creating GUI instance...")
    app = CyberSafeGUI()
    print("✓ GUI instance created")
    
    print("Running app...")
    app.run()
    print("✓ App completed")
    
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
