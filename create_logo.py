#!/usr/bin/env python3
"""
Create CyberSafe Logo from scratch
Generates both PNG and ICO formats
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_cybersafe_logo():
    """Create CyberSafe logo with branding"""
    
    project_root = Path(__file__).parent
    assets_dir = project_root / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Create high-quality image
    size = (512, 512)
    bg_color = (0, 0, 0)  # Black background
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw simple CS logo (shield shape)
    # Shield outline
    shield_x = 100
    shield_y = 100
    shield_w = 312
    shield_h = 312
    
    # Draw shield shape
    shield_points = [
        (shield_x + shield_w/2, shield_y),  # Top center
        (shield_x + shield_w, shield_y + shield_h/3),  # Top right
        (shield_x + shield_w, shield_y + shield_h*0.7),  # Right middle
        (shield_x + shield_w/2, shield_y + shield_h),  # Bottom
        (shield_x, shield_y + shield_h*0.7),  # Left middle
        (shield_x, shield_y + shield_h/3),  # Top left
    ]
    
    # Draw shield with white outline
    draw.polygon(shield_points, outline=(255, 255, 255), width=4)
    
    # Draw inner shield
    inner_points = [
        (shield_x + shield_w/2, shield_y + 20),
        (shield_x + shield_w - 20, shield_y + shield_h/3),
        (shield_x + shield_w - 20, shield_y + shield_h*0.7),
        (shield_x + shield_w/2, shield_y + shield_h - 20),
        (shield_x + 20, shield_y + shield_h*0.7),
        (shield_x + 20, shield_y + shield_h/3),
    ]
    
    draw.polygon(inner_points, fill=(0, 212, 255))  # Cyan fill
    
    # Draw "CS" text in center
    try:
        # Try to use system font
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    text = "CS"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    text_x = (size[0] - text_w) / 2
    text_y = (size[1] - text_h) / 2
    
    draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)
    
    # Save as PNG
    png_path = assets_dir / "cybersafe_logo.png"
    img.save(png_path, format='PNG')
    print(f"✅ PNG Logo created: {png_path}")
    
    # Create ICO versions at different sizes
    ico_path = assets_dir / "cybersafe_logo.ico"
    
    # Create different sized versions
    icon_sizes = [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256)]
    icon_images = []
    
    for size_tuple in icon_sizes:
        resized = img.resize(size_tuple, Image.Resampling.LANCZOS)
        icon_images.append(resized)
    
    # Save as ICO
    icon_images[0].save(ico_path, format='ICO', sizes=icon_sizes)
    print(f"✅ ICO Logo created: {ico_path}")
    
    # Also save as SVG reference
    svg_path = assets_dir / "cybersafe_logo.svg"
    with open(svg_path, 'w') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="512" height="512" fill="#000000"/>
  
  <!-- Shield -->
  <polygon points="256,100 400,170 400,330 256,450 112,330 112,170" 
           fill="#00D4FF" stroke="#FFFFFF" stroke-width="3"/>
  
  <!-- CS Text -->
  <text x="256" y="320" font-family="Arial" font-size="120" font-weight="bold" 
        fill="#000000" text-anchor="middle">CS</text>
  
  <!-- CyberSafe Text -->
  <text x="256" y="470" font-family="Arial" font-size="32" font-weight="bold" 
        fill="#00D4FF" text-anchor="middle">CyberSafe</text>
</svg>''')
    print(f"✅ SVG Logo created: {svg_path}")
    
    return True

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════╗")
    print("║     CyberSafe Logo Generator (PNG, ICO, SVG)           ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    create_cybersafe_logo()
    print("\n✨ Logo generation complete!")
    print("   Files ready in: ./assets/")
