"""
Generates all MAGI indicator images + animation frame sequences.
States: idle (static), thinking (pulsing glow frames), speaking (rotating scan line frames)
Run: python generate_indicators.py
"""
from PIL import Image, ImageDraw
import math
import os

SIZE = 150
BG = (10, 10, 10)
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

PERSONALITIES = [
    ("MELCHIOR",  (0, 212, 255)),
    ("BALTHASAR", (255, 140, 0)),
    ("CASPER",    (0, 255, 136)),
]

THINKING_FRAMES = 12   # smooth pulse cycle
SPEAKING_FRAMES = 16   # full scanner rotation


def draw_base(draw, cx, cy, color, glow_intensity=0.0, scan_angle=None):
    """Draw the indicator badge onto an ImageDraw context."""
    ring_r = 58
    inner_r = 44

    # Glow layers
    if glow_intensity > 0:
        for i in range(10, 0, -1):
            alpha = glow_intensity * (i / 10) * 0.3
            gc = tuple(min(255, int(c * alpha)) for c in color)
            r = ring_r + i * 3
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=gc)

    # Ring
    ring_brightness = max(0.15, glow_intensity)
    rc = tuple(min(255, int(c * ring_brightness)) for c in color)
    draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
                 outline=rc, width=3 if glow_intensity > 0.3 else 1)

    # Inner fill
    inner_color = tuple(min(255, int(c * 0.12 * (1 + glow_intensity))) for c in color)
    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                 fill=inner_color)

    # Center circuit icon
    ic = tuple(min(255, int(c * ring_brightness)) for c in color)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=ic)
    for angle in [90, 210, 330]:
        rad = math.radians(angle)
        ex = int(cx + 22 * math.cos(rad))
        ey = int(cy - 22 * math.sin(rad))
        draw.line([cx, cy, ex, ey], fill=ic, width=2)
        draw.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=ic)

    # Scanner line (speaking state)
    if scan_angle is not None:
        scan_brightness = min(1.0, glow_intensity + 0.4)
        sc = tuple(min(255, int(c * scan_brightness)) for c in color)
        rad = math.radians(scan_angle)
        ex = int(cx + inner_r * math.cos(rad))
        ey = int(cy - inner_r * math.sin(rad))
        draw.line([cx, cy, ex, ey], fill=sc, width=2)
        # Trailing line (faded)
        for trail in range(1, 5):
            trail_rad = math.radians(scan_angle - trail * 15)
            tex = int(cx + inner_r * math.cos(trail_rad))
            tey = int(cy - inner_r * math.sin(trail_rad))
            fade = tuple(min(255, int(c * scan_brightness * (1 - trail * 0.2))) for c in color)
            draw.line([cx, cy, tex, tey], fill=fade, width=1)


def make_frame(name, color, glow_intensity=0.0, scan_angle=None):
    img = Image.new("RGB", (SIZE, SIZE), BG)
    draw = ImageDraw.Draw(img)
    cx, cy = SIZE // 2, SIZE // 2
    draw_base(draw, cx, cy, color, glow_intensity, scan_angle)
    # Name label
    label_brightness = max(0.25, glow_intensity)
    lc = tuple(min(255, int(c * label_brightness)) for c in color)
    total_w = len(name) * 6
    draw.text((cx - total_w // 2, SIZE - 18), name, fill=lc)
    return img


print("Generating MAGI indicators + animation frames...")

for name, color in PERSONALITIES:
    n = name.lower()

    # Static idle
    img = make_frame(name, color, glow_intensity=0.15)
    img.save(os.path.join(IMAGES_DIR, f"{n}_idle.png"))

    # Static active (bright)
    img = make_frame(name, color, glow_intensity=1.0)
    img.save(os.path.join(IMAGES_DIR, f"{n}_active.png"))

    # Thinking animation frames — sine-wave glow pulse
    for i in range(THINKING_FRAMES):
        intensity = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(2 * math.pi * i / THINKING_FRAMES))
        frame = make_frame(name, color, glow_intensity=intensity)
        frame.save(os.path.join(IMAGES_DIR, f"{n}_thinking_{i:02d}.png"))

    # Speaking animation frames — rotating scanner + pulse
    for i in range(SPEAKING_FRAMES):
        angle = (360 / SPEAKING_FRAMES) * i
        intensity = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(2 * math.pi * i / SPEAKING_FRAMES))
        frame = make_frame(name, color, glow_intensity=intensity, scan_angle=angle)
        frame.save(os.path.join(IMAGES_DIR, f"{n}_speaking_{i:02d}.png"))

    print(f"  {name}: idle, active, {THINKING_FRAMES} thinking frames, {SPEAKING_FRAMES} speaking frames")

print("Done.")
