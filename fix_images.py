"""
Force all indicator images onto a guaranteed flat #0a0a0a background.
Run once. Fixes any white/gray/wrong background the image generator produced.
"""
from PIL import Image
import os

BG_COLOR = (10, 10, 10)  # #0a0a0a
IMAGES_DIR = "images"

INDICATORS = [
    "melchior_idle.png",
    "melchior_active.png",
    "balthasar_idle.png",
    "balthasar_active.png",
    "casper_idle.png",
    "casper_active.png",
]

def fix_background(path):
    img = Image.open(path).convert("RGBA")

    # Create a flat #0a0a0a canvas of the same size
    bg = Image.new("RGBA", img.size, BG_COLOR + (255,))

    # Composite the original image over the flat background
    # If the image has transparency, it blends correctly.
    # If not (white/opaque background), detect and replace.
    # Strategy: flood-fill detect corner color as background, make transparent first.
    
    # Sample corners to identify background color
    w, h = img.size
    corners = [
        img.getpixel((0, 0)),
        img.getpixel((w - 1, 0)),
        img.getpixel((0, h - 1)),
        img.getpixel((w - 1, h - 1)),
    ]
    
    # Find the most common corner color (that color = background)
    from collections import Counter
    bg_pixel = Counter(c[:3] for c in corners).most_common(1)[0][0]
    
    # If background is not already near-black, make it transparent before compositing
    if bg_pixel[0] > 30 or bg_pixel[1] > 30 or bg_pixel[2] > 30:
        data = img.getdata()
        new_data = []
        tolerance = 40
        for pixel in data:
            r, g, b = pixel[0], pixel[1], pixel[2]
            # Replace pixels close to the detected background color with transparency
            if (abs(r - bg_pixel[0]) < tolerance and
                abs(g - bg_pixel[1]) < tolerance and
                abs(b - bg_pixel[2]) < tolerance):
                new_data.append((r, g, b, 0))  # transparent
            else:
                new_data.append(pixel)
        img.putdata(new_data)

    # Composite onto guaranteed #0a0a0a background
    bg.paste(img, (0, 0), img)
    result = bg.convert("RGB")
    result.save(path)
    print(f"  Fixed: {os.path.basename(path)} (detected bg: {bg_pixel})")

print("Fixing all indicator backgrounds to #0a0a0a...")
for fname in INDICATORS:
    fpath = os.path.join(IMAGES_DIR, fname)
    if os.path.exists(fpath):
        fix_background(fpath)
    else:
        print(f"  MISSING: {fpath}")

print("Done.")
