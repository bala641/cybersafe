#!/usr/bin/env python3
"""
CyberSafe Installation Tracker
Tracks download and installation events for analytics
"""

import sys
import os
import json
import socket
import platform
import uuid
from datetime import datetime
from pathlib import Path

# Add core to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.user_tracker import UserTracker, track_first_launch
except ImportError:
    # Fallback if core module not available
    class UserTracker:
        def track_download(self, *args, **kwargs):
            pass
        def track_first_launch(self):
            pass


def track_installation():
    """Track the installation process"""
    try:
        tracker = UserTracker()
        
        # Track download event
        tracker.track_download('CyberSafe-Installer.exe')
        print("[Analytics] Download tracked")
        
        # Track first launch
        tracker.track_first_launch()
        print("[Analytics] First launch tracked")
        
        return True
    except Exception as e:
        print(f"[Analytics] Warning: Could not track installation ({e})")
        return False


def main():
    """Main entry point for install tracking"""
    print("\n" + "="*60)
    print("CyberSafe Installation & Setup")
    print("="*60 + "\n")
    
    # Track the installation
    success = track_installation()
    
    if success:
        print("\n[✓] Analytics enabled - Installation tracked successfully\n")
    else:
        print("\n[⚠] Analytics tracking disabled\n")
    
    print("Starting CyberSafe...\n")
    
    # Import and run main
    try:
        from main import main as app_main
        return app_main()
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
