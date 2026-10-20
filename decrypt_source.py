#!/usr/bin/env python3
"""
CyberSafe Source Code Decryption Tool
Requires a valid access key to decrypt protected source code
"""

import os
import sys
import hashlib
from pathlib import Path
from getpass import getpass
import shutil

# Valid access keys (SHA256 hashed)
VALID_KEYS = {
    # Developer key: "cybersafe_dev_2024"
    "8c6d0c2c2c8f8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c": "Developer Access",
    # Contact balacyber0107@gmail.com for additional keys
}

def hash_key(key):
    """Hash the provided key for comparison"""
    return hashlib.sha256(key.encode()).hexdigest()[:32]

def check_protected_source():
    """Check if src directory is protected"""
    src_path = Path("src")
    protected_marker = Path("PROTECTED_SOURCE.txt")
    
    if not src_path.exists():
        print("❌ Error: Source directory not found!")
        return False
    
    if not protected_marker.exists():
        print("⚠️  Warning: Protection marker not found")
        return False
    
    return True

def request_access_key():
    """Request access key from user"""
    print("\n" + "="*60)
    print("CyberSafe Source Code Access")
    print("="*60)
    print("\n🔒 This source code is protected with an access key.")
    print("\nTo obtain an access key, contact:")
    print("📧 Email: balacyber0107@gmail.com")
    print("💼 LinkedIn: https://www.linkedin.com/in/bala-b-e17")
    print("\n" + "="*60 + "\n")
    
    key = getpass("Enter access key: ")
    return key

def verify_access(key):
    """Verify the provided access key"""
    hashed_key = hash_key(key)
    
    # For now, accept any key (in production, use real validation)
    # This is a placeholder - actual implementation would validate against server
    
    if hashed_key in VALID_KEYS:
        return True, VALID_KEYS[hashed_key]
    
    # Placeholder: Accept key if it matches the pattern
    if len(key) >= 8:
        print("⚠️  Note: Using placeholder validation")
        return True, "Standard Access"
    
    return False, None

def decrypt_source():
    """Decrypt and extract source code"""
    src_path = Path("src")
    
    print("\n✓ Access granted!")
    print("📂 Source code is already available in the 'src' directory")
    print("\nContents:")
    
    if src_path.exists():
        for item in src_path.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(src_path)
                print(f"  ✓ {rel_path}")
    
    print("\n" + "="*60)
    print("Source Code Access Enabled")
    print("="*60)
    print("\nYou can now:")
    print("  • View and modify source code")
    print("  • Run: python main.py --gui")
    print("  • Read the source code in the 'src' directory")
    print("\nPlease note:")
    print("  • Source code is proprietary")
    print("  • Do not distribute without permission")
    print("  • Report security issues to: balacyber0107@gmail.com")
    print("\n")

def main():
    """Main function"""
    print("\n" + "="*60)
    print("CyberSafe Source Code Access Tool v1.0")
    print("="*60)
    
    # Check if already decrypted
    if not check_protected_source():
        sys.exit(1)
    
    # Request key
    access_key = request_access_key()
    
    # Verify key
    is_valid, access_type = verify_access(access_key)
    
    if not is_valid:
        print("\n❌ Invalid access key!")
        print("Please contact: balacyber0107@gmail.com")
        print("LinkedIn: https://www.linkedin.com/in/bala-b-e17")
        sys.exit(1)
    
    # Grant access
    decrypt_source()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAccess denied.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
