#!/usr/bin/env python3
"""
Convert CyberSafe logo PNG to ICO format
Place your logo.png in the same folder and run this script
"""

from PIL import Image
import os
from pathlib import Path

def convert_png_to_ico():
    """Convert PNG logo to ICO format"""
    
    project_root = Path(__file__).parent
    assets_dir = project_root / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Look for logo in common locations
    logo_paths = [
        project_root / "logo.png",
        project_root / "cybersafe_logo.png",
        project_root / "cybersafe.png",
        project_root / "logo",
        assets_dir / "logo.png",
    ]
    
    logo_file = None
    for path in logo_paths:
        if path.exists():
            logo_file = path
            print(f"Found logo: {logo_file}")
            break
    
    if not logo_file:
        print("❌ Logo file not found!")
        print("\nTo use your logo:")
        print("1. Place your logo file (PNG) in this folder")
        print("2. Name it: logo.png")
        print("3. Run this script again")
        print("\nSupported formats: PNG, JPG, BMP")
        print(f"\nSearched in: {project_root}")
        return False
    
    try:
        # Open image
        img = Image.open(logo_file)
        
        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Resize to standard icon sizes
        sizes = [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256)]
        
        # Create ICO file
        ico_path = assets_dir / "cybersafe_logo.ico"
        
        # Resize image to fit in ICO
        img.thumbnail((256, 256), Image.Resampling.LANCZOS)
        
        # Save as ICO
        img.save(ico_path, format='ICO', sizes=sizes)
        
        print(f"✅ Logo converted successfully!")
        print(f"   Saved to: {ico_path}")
        
        # Also create PNG versions for web
        png_path = assets_dir / "cybersafe_logo.png"
        img.save(png_path, format='PNG')
        print(f"   Web version: {png_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error converting logo: {e}")
        return False

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════╗")
    print("║        CyberSafe Logo Converter (PNG → ICO)            ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    convert_png_to_ico()
