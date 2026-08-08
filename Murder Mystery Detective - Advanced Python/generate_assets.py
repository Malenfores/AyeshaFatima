"""
generate_assets.py
-------------------
Builds every image and sound file used by the Murder Mystery Detective game.

This is a ONE-TIME build script (needs Pillow). It is included in the project
so you can regenerate / customize the art & sound style later, but the
finished game (detective_game.py) does NOT need Pillow to run - it only
needs the PNG/WAV files this script produces, which are already shipped
inside assets/.

Run:  python generate_assets.py
"""

import math
import os
import random
import struct
import wave

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

random.seed(7)

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, "assets", "images")
SND_DIR = os.path.join(BASE, "assets", "sounds")
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(SND_DIR, exist_ok=True)

W, H = 1000, 640


# =====================================================================
# IMAGE HELPERS
# =====================================================================

def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def vertical_gradient(size, top_color, bottom_color):
    w, h = size
    img = Image.new("RGB", size, top_color)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        col = lerp_color(top_color, bottom_color, t)
        for x in range(0, w, 4):  # step for speed, then stretch
            px[x, y] = col
    # fill in the skipped columns quickly
    img = img.resize((w // 4, h), Image.NEAREST).resize((w, h), Image.BILINEAR)
    return img


def diagonal_gradient(size, c1, c2):
    w, h = size
    base = Image.new("L", (w, h))
    px = base.load()
    maxd = w + h
    for y in range(h):
        for x in range(0, w, 3):
            t = (x + y) / maxd
            px[x, y] = int(255 * t)
    base = base.resize((w // 3, h), Image.NEAREST).resize((w, h), Image.BILINEAR)
    grad = Image.merge("RGB", [base.point(lambda p: int(lerp(c1[i], c2[i], p / 255))) for i in range(3)])
    return grad


def add_vignette(img, strength=180):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([-w * 0.25, -h * 0.25, w * 1.25, h * 1.25], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w // 6))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    out = Image.composite(img, dark, mask.point(lambda p: 255 - int(strength * (255 - p) / 255)))
    return out


def add_grain(img, amount=10):
    w, h = img.size
    noise = Image.effect_noise((w, h), amount).convert("L")
    noise_rgb = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(img, noise_rgb, 0.035)


def add_rain(img, n=140, color=(210, 220, 235), alpha=70):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for _ in range(n):
        x = random.randint(0, w)
        y = random.randint(0, h)
        length = random.randint(14, 34)
        d.line([(x, y), (x - 4, y + length)], fill=color + (alpha,), width=1)
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.4))
    base = img.convert("RGBA")
    return Image.alpha_composite(base, overlay).convert("RGB")


def add_light_beams(img, cx, cy, color=(255, 220, 150), n=5, alpha=26):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(n):
        ang = math.radians(-70 + i * 10)
        length = 900
        x2 = cx + length * math.cos(ang)
        y2 = cy + length * math.sin(ang)
        width_ang = math.radians(3)
        x2a = cx + length * math.cos(ang - width_ang)
        y2a = cy + length * math.sin(ang - width_ang)
        x2b = cx + length * math.cos(ang + width_ang)
        y2b = cy + length * math.sin(ang + width_ang)
        d.polygon([(cx, cy), (x2a, y2a), (x2b, y2b)], fill=color + (alpha,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(18))
    base = img.convert("RGBA")
    return Image.alpha_composite(base, overlay).convert("RGB")


def moon(img, cx, cy, r, color=(235, 235, 210)):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (255,))
    glow = overlay.filter(ImageFilter.GaussianBlur(r // 2))
    base = img.convert("RGBA")
    base = Image.alpha_composite(base, glow)
    base = Image.alpha_composite(base, overlay)
    return base.convert("RGB")


def silhouette_building(draw, x, y, w, h, color):
    draw.rectangle([x, y, x + w, y + h], fill=color)
    # windows removed for a clean silhouette look


def city_skyline(img, color=(10, 10, 18), horizon=560):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    x = -20
    while x < w + 20:
        bw = random.randint(40, 90)
        bh = random.randint(80, 260)
        d.rectangle([x, horizon - bh, x + bw, horizon + 40], fill=color + (255,))
        x += bw + random.randint(4, 14)
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def mansion_silhouette(img, color=(8, 6, 12), horizon=600):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    cx = w * 0.5
    d.rectangle([cx - 300, horizon - 180, cx + 300, horizon + 60], fill=color + (255,))
    d.polygon([(cx - 320, horizon - 180), (cx, horizon - 320), (cx + 320, horizon - 180)], fill=color + (255,))
    d.rectangle([cx - 60, horizon - 300, cx - 20, horizon - 200], fill=color + (255,))
    for tx in (cx - 260, cx + 230):
        d.rectangle([tx, horizon - 260, tx + 55, horizon + 60], fill=color + (255,))
        d.polygon([(tx - 8, horizon - 260), (tx + 27, horizon - 320), (tx + 63, horizon - 260)], fill=color + (255,))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def bookshelf_pattern(img, color=(30, 18, 10), horizon=0):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    shelf_h = 46
    y = 40
    book_colors = [(120, 40, 30), (30, 70, 90), (90, 70, 20), (60, 30, 70), (20, 70, 40)]
    while y < h - 40:
        x = 30
        while x < w - 30:
            bw = random.randint(10, 22)
            bh = random.randint(shelf_h - 14, shelf_h)
            c = random.choice(book_colors)
            d.rectangle([x, y + (shelf_h - bh), x + bw, y + shelf_h], fill=c + (150,))
            x += bw + 2
        d.rectangle([20, y + shelf_h, w - 20, y + shelf_h + 6], fill=color + (200,))
        y += shelf_h + 26
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB").filter(ImageFilter.GaussianBlur(1))


def explosion_burst(img, cx, cy, color=(255, 150, 40)):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(60):
        ang = random.uniform(0, math.tau)
        r1 = random.uniform(10, 40)
        r2 = r1 + random.uniform(60, 260)
        x1, y1 = cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)
        x2, y2 = cx + r2 * math.cos(ang), cy + r2 * math.sin(ang)
        d.line([(x1, y1), (x2, y2)], fill=color + (40,), width=random.randint(2, 5))
    d.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill=color + (60,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(6))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def radar_sweep(img, cx, cy, r, color=(80, 220, 200)):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(1, 5):
        rr = r * i / 4
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=color + (90,), width=2)
    d.pieslice([cx - r, cy - r, cx + r, cy + r], -20, 20, fill=color + (35,))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def waves(img, y0, color=(20, 60, 90)):
    w, h = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for row in range(6):
        yy = y0 + row * 34
        pts = []
        for x in range(0, w + 20, 20):
            yy2 = yy + 10 * math.sin(x / 45 + row)
            pts.append((x, yy2))
        pts += [(w, h), (0, h)]
        alpha = 140 - row * 18
        d.polygon(pts, fill=color + (max(20, alpha),))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def vault_circle(img, cx, cy, r, color=(40, 200, 120)):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color + (180,), width=10)
    d.ellipse([cx - r + 26, cy - r + 26, cx + r - 26, cy + r - 26], outline=color + (100,), width=4)
    for a in range(0, 360, 30):
        rad = math.radians(a)
        x1, y1 = cx + (r - 26) * math.cos(rad), cy + (r - 26) * math.sin(rad)
        x2, y2 = cx + r * math.cos(rad), cy + r * math.sin(rad)
        d.line([(x1, y1), (x2, y2)], fill=color + (150,), width=4)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=color + (255,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(1))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def medical_cross(img, cx, cy, size, color=(140, 220, 220)):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    t = size / 3
    d.rectangle([cx - t / 2, cy - size / 2, cx + t / 2, cy + size / 2], fill=color + (110,))
    d.rectangle([cx - size / 2, cy - t / 2, cx + size / 2, cy + t / 2], fill=color + (110,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(8))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def fingerprint(img, cx, cy, r, color=(212, 175, 55), alpha=90):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(16):
        rr = r * (i + 1) / 16
        bbox = [cx - rr, cy - rr * 1.15, cx + rr, cy + rr * 1.15]
        d.arc(bbox, 25, 335, fill=color + (alpha,), width=3)
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def magnifier(img, cx, cy, r, color=(212, 175, 55)):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color + (255,), width=10)
    hx, hy = cx + r * 0.75, cy + r * 0.75
    d.line([(hx, hy), (hx + r * 0.9, hy + r * 0.9)], fill=color + (255,), width=16)
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def crack_lines(img, n=6, color=(255, 255, 255), alpha=30):
    w, h = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for _ in range(n):
        x, y = random.randint(0, w), 0
        for _ in range(6):
            nx = x + random.randint(-60, 60)
            ny = y + random.randint(40, 110)
            d.line([(x, y), (nx, ny)], fill=color + (alpha,), width=2)
            x, y = nx, ny
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.6))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def stars(img, n=90, area=(0, 0, None, 420)):
    w, h = img.size
    x1, y1, x2, y2 = area
    x2 = x2 or w
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for _ in range(n):
        x = random.randint(x1, x2)
        y = random.randint(y1, y2)
        r = random.choice([1, 1, 1, 2])
        a = random.randint(90, 220)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def save(img, name):
    path = os.path.join(IMG_DIR, name)
    img.save(path, "PNG")
    print("wrote", path)


# =====================================================================
# BACKGROUND SCENES
# =====================================================================

def make_title_bg():
    img = diagonal_gradient((W, H), (10, 6, 14), (28, 10, 14))
    img = stars(img, 70, (0, 0, W, 300))
    img = mansion_silhouette(img, color=(4, 3, 6), horizon=680)
    img = fingerprint(img, W * 0.78, H * 0.32, 170, alpha=55)
    img = magnifier(img, W * 0.20, H * 0.30, 90)
    img = add_light_beams(img, W * 0.5, -40, n=6, alpha=18)
    img = add_rain(img, 160)
    img = add_vignette(img, 190)
    img = add_grain(img)
    save(img, "title_bg.png")


def make_menu_bg():
    img = vertical_gradient((W, H), (14, 10, 22), (30, 14, 18))
    img = stars(img, 50, (0, 0, W, 260))
    img = fingerprint(img, W * 0.85, H * 0.75, 200, alpha=40)
    img = add_vignette(img, 170)
    img = add_grain(img)
    save(img, "menu_bg.png")


def make_case1_bg():  # Dark Mansion
    img = vertical_gradient((W, H), (18, 6, 10), (46, 14, 18))
    img = mansion_silhouette(img, color=(6, 4, 7), horizon=650)
    img = crack_lines(img, 5)
    img = add_light_beams(img, W * 0.5, -20, color=(255, 210, 150), n=4, alpha=16)
    img = add_rain(img, 200)
    img = add_vignette(img, 200)
    img = add_grain(img)
    save(img, "case1_bg.png")


def make_case2_bg():  # Hotel Silence
    img = vertical_gradient((W, H), (8, 10, 26), (24, 18, 12))
    img = city_skyline(img, color=(6, 6, 14), horizon=560)
    img = moon(img, W * 0.82, 140, 70, (230, 225, 200))
    img = add_vignette(img, 180)
    img = add_grain(img)
    save(img, "case2_bg.png")


def make_case3_bg():  # University Lab Explosion
    img = vertical_gradient((W, H), (6, 18, 20), (30, 14, 8))
    img = explosion_burst(img, W * 0.5, H * 0.42, color=(255, 140, 40))
    img = explosion_burst(img, W * 0.5, H * 0.42, color=(120, 220, 255))
    img = add_vignette(img, 190)
    img = add_grain(img)
    save(img, "case3_bg.png")


def make_case4_bg():  # Bank Vault
    img = vertical_gradient((W, H), (5, 12, 10), (10, 22, 16))
    img = vault_circle(img, W * 0.5, H * 0.46, 230, color=(60, 220, 140))
    img = add_vignette(img, 210)
    img = add_grain(img)
    save(img, "case4_bg.png")


def make_case5_bg():  # Hospital Night Shift
    img = vertical_gradient((W, H), (10, 18, 22), (22, 30, 32))
    img = medical_cross(img, W * 0.5, H * 0.42, 340, color=(150, 230, 230))
    img = add_vignette(img, 170)
    img = add_grain(img)
    save(img, "case5_bg.png")


def make_case6_bg():  # Airport Midnight
    img = vertical_gradient((W, H), (10, 8, 24), (30, 16, 10))
    img = radar_sweep(img, W * 0.5, H * 0.42, 260, color=(90, 230, 210))
    img = stars(img, 60, (0, 0, W, 250))
    img = add_vignette(img, 190)
    img = add_grain(img)
    save(img, "case6_bg.png")


def make_case7_bg():  # Cruise Ship
    img = vertical_gradient((W, H), (6, 14, 26), (10, 30, 40))
    img = moon(img, W * 0.78, 130, 65, (235, 235, 210))
    img = stars(img, 60, (0, 0, W, 250))
    img = waves(img, H * 0.62, color=(15, 55, 80))
    img = add_vignette(img, 180)
    img = add_grain(img)
    save(img, "case7_bg.png")


def make_case8_bg():  # Old Library
    img = vertical_gradient((W, H), (18, 12, 6), (34, 22, 10))
    img = bookshelf_pattern(img, color=(20, 12, 6))
    img = add_vignette(img, 210)
    img = add_grain(img)
    save(img, "case8_bg.png")


def curtain_drapes(img, color=(40, 8, 14)):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    n = 14
    seg = w / n
    for i in range(n):
        x0 = i * seg
        shade = 30 if i % 2 == 0 else 55
        d.rectangle([x0, 0, x0 + seg, h * 0.55], fill=(color[0] + shade, color[1], color[2], 255))
    overlay = overlay.filter(ImageFilter.GaussianBlur(3))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def spotlight(img, cx, cy, r, color=(255, 235, 180)):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.ellipse([cx - r, cy - r * 1.4, cx + r, cy + r * 1.4], fill=color + (55,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(30))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_case9_bg():  # Theater Backstage
    img = vertical_gradient((W, H), (18, 5, 8), (34, 8, 12))
    img = curtain_drapes(img)
    img = spotlight(img, W * 0.5, H * 0.55, 160)
    img = add_vignette(img, 190)
    img = add_grain(img)
    save(img, "case9_bg.png")


def poker_chips(img, cx, cy):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    colors = [(200, 40, 40), (40, 160, 90), (40, 90, 200), (230, 210, 60)]
    for i in range(18):
        ang = random.uniform(0, math.tau)
        dist = random.uniform(0, 220)
        x = cx + dist * math.cos(ang)
        y = cy * 0.5 + dist * math.sin(ang) * 0.4
        r = random.randint(18, 26)
        c = random.choice(colors)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (210,), outline=(20, 20, 20, 255))
        d.ellipse([x - r + 6, y - r + 6, x + r - 6, y + r - 6], outline=(255, 255, 255, 160), width=2)
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_case10_bg():  # Casino
    img = vertical_gradient((W, H), (10, 6, 2), (30, 16, 4))
    img = poker_chips(img, W * 0.5, H * 0.55)
    img = add_light_beams(img, W * 0.5, -30, color=(255, 200, 100), n=5, alpha=20)
    img = add_vignette(img, 200)
    img = add_grain(img)
    save(img, "case10_bg.png")


def mountain_peaks(img, base_y, color=(230, 235, 245)):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    x = -40
    rng = random.Random(3)
    while x < w + 40:
        peak_w = rng.randint(160, 320)
        peak_h = rng.randint(120, 260)
        d.polygon([(x, base_y), (x + peak_w / 2, base_y - peak_h), (x + peak_w, base_y)],
                  fill=color + (230,))
        x += peak_w * 0.6
    overlay = overlay.filter(ImageFilter.GaussianBlur(1))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_case11_bg():  # Ski Resort
    img = vertical_gradient((W, H), (10, 18, 30), (200, 210, 225))
    img = mountain_peaks(img, H * 0.62)
    img = add_vignette(img, 150)
    img = add_grain(img, 8)
    save(img, "case11_bg.png")


def picture_frames(img, color=(60, 40, 20)):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    positions = [(w * 0.18, h * 0.32, 130, 170), (w * 0.5, h * 0.28, 160, 200), (w * 0.82, h * 0.34, 120, 155)]
    for cx, cy, fw, fh in positions:
        d.rectangle([cx - fw / 2, cy - fh / 2, cx + fw / 2, cy + fh / 2], outline=color + (255,), width=6)
        d.rectangle([cx - fw / 2 + 10, cy - fh / 2 + 10, cx + fw / 2 - 10, cy + fh / 2 - 10],
                     fill=(20, 16, 24, 255))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_case12_bg():  # Art Gallery
    img = vertical_gradient((W, H), (16, 14, 20), (28, 22, 30))
    img = picture_frames(img)
    img = spotlight(img, W * 0.5, H * 0.3, 200)
    img = add_vignette(img, 190)
    img = add_grain(img)
    save(img, "case12_bg.png")


def rail_tracks(img, base_y, color=(20, 20, 24)):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    vp_x, vp_y = w * 0.5, base_y - 260
    for off in (-90, 90):
        d.line([(vp_x, vp_y), (vp_x + off * 3.2, h)], fill=color + (255,), width=6)
    for i in range(14):
        t = i / 14
        y = vp_y + t * (h - vp_y)
        spread = 20 + t * 280
        d.line([(vp_x - spread, y), (vp_x + spread, y)], fill=(40, 34, 30, 220), width=4)
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_case13_bg():  # Night Train
    img = vertical_gradient((W, H), (6, 8, 18), (14, 14, 24))
    img = stars(img, 50, (0, 0, W, int(H * 0.35)))
    img = rail_tracks(img, H * 0.95)
    img = moon(img, W * 0.18, H * 0.16, 40)
    img = add_vignette(img, 190)
    img = add_grain(img)
    save(img, "case13_bg.png")


def sound_waves_motif(img, cx, cy, color=(220, 60, 90)):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(1, 8):
        r = i * 26
        d.arc([cx - r, cy - r, cx + r, cy + r], -50, 50, fill=color + (170,), width=4)
        d.arc([cx - r, cy - r, cx + r, cy + r], 130, 230, fill=color + (170,), width=4)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=color + (255,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(1))
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_case14_bg():  # Radio Station
    img = vertical_gradient((W, H), (14, 4, 10), (26, 6, 14))
    img = sound_waves_motif(img, W * 0.5, H * 0.45)
    img = add_vignette(img, 200)
    img = add_grain(img)
    save(img, "case14_bg.png")


def make_result_bgs():
    win = vertical_gradient((W, H), (6, 22, 10), (10, 34, 14))
    win = add_light_beams(win, W * 0.5, -20, color=(255, 230, 140), n=6, alpha=22)
    win = add_vignette(win, 170)
    win = add_grain(win)
    save(win, "result_win_bg.png")

    lose = vertical_gradient((W, H), (26, 6, 6), (40, 10, 10))
    lose = crack_lines(lose, 8)
    lose = add_vignette(lose, 190)
    lose = add_grain(lose)
    save(lose, "result_lose_bg.png")


# =====================================================================
# SUSPECT AVATARS (procedural silhouette portraits, no real people)
# =====================================================================

AVATAR_PALETTE = [
    (176, 58, 46), (52, 73, 94), (39, 132, 108), (142, 68, 173),
    (211, 141, 32), (44, 62, 80), (95, 39, 205), (26, 118, 108),
]


def make_avatar(i, color):
    size = 260
    img = Image.new("RGB", (size, size), (18, 18, 22))
    d = ImageDraw.Draw(img)
    # background plaque
    d.rectangle([0, 0, size, size], fill=(22, 22, 26))
    for y in range(size):
        t = y / size
        c = lerp_color((28, 28, 34), (14, 14, 18), t)
        d.line([(0, y), (size, y)], fill=c)
    # bust silhouette
    cx, cy = size // 2, size // 2 + 10
    d.ellipse([cx - 55, cy - 95, cx + 55, cy - 5], fill=color)  # head
    d.pieslice([cx - 95, cy - 10, cx + 95, cy + 170], 180, 360, fill=color)  # shoulders
    # simple hat brim for noir vibe on alternating avatars
    if i % 2 == 0:
        d.rectangle([cx - 65, cy - 100, cx + 65, cy - 84], fill=(15, 15, 18))
        d.rectangle([cx - 40, cy - 118, cx + 40, cy - 98], fill=(15, 15, 18))
    img = img.filter(ImageFilter.SMOOTH)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, size - 1, size - 1], outline=(212, 175, 55), width=4)
    save(img, f"avatar_{i}.png")


def make_avatars():
    for i, color in enumerate(AVATAR_PALETTE):
        make_avatar(i, color)


# =====================================================================
# ICONS
# =====================================================================

def make_icon_badge():
    size = 200
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    pts = []
    for i in range(14):
        ang = math.tau * i / 14
        r = 88 if i % 2 == 0 else 70
        pts.append((cx + r * math.sin(ang), cy - r * math.cos(ang)))
    d.polygon(pts, fill=(212, 175, 55, 255))
    d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=(30, 20, 10, 255))
    d.ellipse([cx - 45, cy - 45, cx + 45, cy + 45], outline=(212, 175, 55, 255), width=4)
    save(img, "icon_badge.png")


def make_icon_magnifier():
    size = 160
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([20, 20, 100, 100], outline=(230, 230, 230, 255), width=10)
    d.line([(90, 90), (140, 140)], fill=(230, 230, 230, 255), width=14)
    save(img, "icon_magnifier.png")


# =====================================================================
# SOUND SYNTHESIS  (pure stdlib: wave + struct + math)
# =====================================================================

FRAMERATE = 22050


def _envelope(n, attack=0.05, release=0.3):
    a = int(n * attack)
    r = int(n * release)
    env = []
    for i in range(n):
        if i < a:
            env.append(i / max(1, a))
        elif i > n - r:
            env.append(max(0.0, (n - i) / max(1, r)))
        else:
            env.append(1.0)
    return env


def _tone(freq, dur, vol=0.4, wave_type="sine", attack=0.05, release=0.4):
    n = int(FRAMERATE * dur)
    env = _envelope(n, attack, release)
    samples = []
    for i in range(n):
        t = i / FRAMERATE
        if wave_type == "sine":
            v = math.sin(2 * math.pi * freq * t)
        elif wave_type == "square":
            v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif wave_type == "saw":
            v = 2 * ((freq * t) % 1) - 1
        elif wave_type == "noise":
            v = random.uniform(-1, 1)
        else:
            v = math.sin(2 * math.pi * freq * t)
        samples.append(v * env[i] * vol)
    return samples


def _mix(*tracks):
    n = max(len(t) for t in tracks)
    out = [0.0] * n
    for t in tracks:
        for i, v in enumerate(t):
            out[i] += v
    peak = max(1e-6, max(abs(v) for v in out))
    if peak > 1.0:
        out = [v / peak for v in out]
    return out


def _concat_with_gap(*tracks, gap=0.02):
    gap_samples = [0.0] * int(FRAMERATE * gap)
    out = []
    for i, t in enumerate(tracks):
        out.extend(t)
        if i != len(tracks) - 1:
            out.extend(gap_samples)
    return out


def write_wav(samples, name):
    path = os.path.join(SND_DIR, name)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(FRAMERATE)
        frames = bytearray()
        for s in samples:
            s = max(-1.0, min(1.0, s))
            frames.extend(struct.pack("<h", int(s * 32767)))
        f.writeframes(bytes(frames))
    print("wrote", path)


def make_sounds():
    # UI click
    write_wav(_tone(880, 0.06, vol=0.35, wave_type="square", attack=0.01, release=0.6), "click.wav")

    # clue found - bright rising chime
    a = _tone(660, 0.12, vol=0.3, attack=0.02, release=0.5)
    b = _tone(880, 0.12, vol=0.3, attack=0.02, release=0.5)
    c = _tone(1320, 0.18, vol=0.32, attack=0.02, release=0.6)
    write_wav(_concat_with_gap(a, b, c, gap=0.015), "clue.wav")

    # correct accusation - triumphant major arpeggio
    notes = [523, 659, 784, 1046]
    parts = [_tone(f, 0.16, vol=0.32, attack=0.01, release=0.55) for f in notes]
    chord = _mix(*[_tone(f, 0.5, vol=0.18, attack=0.02, release=0.7) for f in notes])
    write_wav(_concat_with_gap(*parts, gap=0.01) + chord, "correct.wav")

    # wrong accusation - low descending buzzer
    a = _tone(220, 0.18, vol=0.35, wave_type="saw", attack=0.01, release=0.4)
    b = _tone(160, 0.22, vol=0.35, wave_type="saw", attack=0.01, release=0.4)
    c = _tone(110, 0.35, vol=0.38, wave_type="saw", attack=0.01, release=0.5)
    write_wav(_concat_with_gap(a, b, c, gap=0.02), "wrong.wav")

    # case intro sting - ominous low drone with a bell hit
    drone = _tone(65, 1.6, vol=0.25, wave_type="sine", attack=0.3, release=1.0)
    bell = _tone(440, 1.2, vol=0.18, wave_type="sine", attack=0.01, release=1.0)
    write_wav(_mix(drone, bell), "intro_sting.wav")

    # page turn / notebook
    write_wav(_tone(300, 0.08, vol=0.2, wave_type="noise", attack=0.01, release=0.5), "page.wav")

    # victory fanfare (longer, for full game complete)
    notes = [523, 659, 784, 1046, 784, 1046, 1318]
    parts = [_tone(f, 0.18, vol=0.3, attack=0.01, release=0.5) for f in notes]
    write_wav(_concat_with_gap(*parts, gap=0.01), "fanfare.wav")

    # ---- ambient background loop: moody detective/murder-mystery atmosphere
    # low twin-drone (slightly detuned for tension) + soft heartbeat pulses +
    # a faint distant clock tick. Loops seamlessly (loop_seconds long).
    loop_seconds = 12.0
    n = int(FRAMERATE * loop_seconds)

    drone = [0.0] * n
    for i in range(n):
        t = i / FRAMERATE
        wobble = 1 + 0.004 * math.sin(2 * math.pi * 0.05 * t)
        v = 0.10 * math.sin(2 * math.pi * 54 * wobble * t)
        v += 0.07 * math.sin(2 * math.pi * 54.6 * wobble * t)
        # slow swell so the loop doesn't feel static
        swell = 0.7 + 0.3 * math.sin(2 * math.pi * (1 / loop_seconds) * t)
        drone[i] = v * swell

    # heartbeat: two soft low thumps repeating every ~2.2s
    heartbeat = [0.0] * n
    beat_period = 2.2
    t = 0.06
    while t < loop_seconds:
        for offset, vol in ((0.0, 0.16), (0.18, 0.11)):
            start = t + offset
            if start >= loop_seconds:
                continue
            dur = 0.12
            m = int(FRAMERATE * dur)
            s0 = int(FRAMERATE * start)
            for i in range(m):
                if s0 + i >= n:
                    break
                tt = i / FRAMERATE
                env = math.exp(-tt * 26)
                heartbeat[s0 + i] += vol * env * math.sin(2 * math.pi * 62 * tt)
        t += beat_period

    # distant clock tick every ~1.5s, very quiet
    tick = [0.0] * n
    tt_period = 1.5
    t = 0.9
    while t < loop_seconds:
        s0 = int(FRAMERATE * t)
        m = int(FRAMERATE * 0.03)
        for i in range(m):
            if s0 + i >= n:
                break
            env = math.exp(-(i / FRAMERATE) * 140)
            tick[s0 + i] += 0.05 * env * (1 if random.random() > 0.5 else -1)
        t += tt_period

    ambient = _mix(drone, heartbeat, tick)
    # gentle fade in/out at the loop boundaries so looping feels seamless
    fade_n = int(FRAMERATE * 0.8)
    for i in range(fade_n):
        f = i / fade_n
        ambient[i] *= f
        ambient[n - 1 - i] *= f
    write_wav(ambient, "ambient_murder.mp3")

    # ---- horror jump-scare stinger: sharp dissonant stab, used sparingly
    # while investigating to keep the "horror detective" tension alive
    stab1 = _tone(196, 0.5, vol=0.5, wave_type="sawtooth", attack=0.001, release=0.7)
    stab2 = _tone(207, 0.5, vol=0.4, wave_type="sawtooth", attack=0.001, release=0.7)  # dissonant interval
    sub = _tone(55, 0.6, vol=0.4, wave_type="square", attack=0.001, release=0.8)
    hiss_n = int(FRAMERATE * 0.35)
    hiss = [random.uniform(-1, 1) * 0.15 * math.exp(-3 * (i / hiss_n)) for i in range(hiss_n)]
    stinger = _mix(stab1, stab2, sub, hiss)
    write_wav(stinger, "horror_stinger.wav")

    # ---- notification: short, pleasant two-note blip (distinct from click)
    n1 = _tone(740, 0.06, vol=0.28, attack=0.005, release=0.5)
    n2 = _tone(988, 0.09, vol=0.3, attack=0.005, release=0.5)
    write_wav(_concat_with_gap(n1, n2, gap=0.02), "notification.wav")

    # ---- door creak: low-to-high frequency sweep approximated by two tones
    d1 = _tone(90, 0.35, vol=0.22, wave_type="sawtooth", attack=0.05, release=0.6)
    d2 = _tone(140, 0.3, vol=0.16, wave_type="sawtooth", attack=0.08, release=0.5)
    write_wav(_mix(d1, d2), "door.wav")

    # ---- footstep: two soft low thumps
    f1 = _tone(90, 0.09, vol=0.3, wave_type="square", attack=0.005, release=0.55)
    f2 = _tone(80, 0.09, vol=0.26, wave_type="square", attack=0.005, release=0.55)
    write_wav(_concat_with_gap(f1, f2, gap=0.16), "footstep.wav")

    # ---- interrogation chime: questioning two-tone (up-down)
    q1 = _tone(523, 0.1, vol=0.28, attack=0.01, release=0.5)
    q2 = _tone(440, 0.16, vol=0.26, attack=0.01, release=0.55)
    write_wav(_concat_with_gap(q1, q2, gap=0.03), "interrogation.wav")

    # ---- menu theme: gentle, mellow looping bed for menu/records/settings screens
    menu_loop_seconds = 9.0
    mn = int(FRAMERATE * menu_loop_seconds)
    menu_drone = [0.0] * mn
    for i in range(mn):
        t = i / FRAMERATE
        wobble = 1 + 0.003 * math.sin(2 * math.pi * 0.08 * t)
        v = 0.08 * math.sin(2 * math.pi * 110 * wobble * t)
        v += 0.05 * math.sin(2 * math.pi * 164.8 * wobble * t)  # soft fifth
        swell = 0.75 + 0.25 * math.sin(2 * math.pi * (1 / menu_loop_seconds) * t)
        menu_drone[i] = v * swell
    fade_n2 = int(FRAMERATE * 0.6)
    for i in range(fade_n2):
        f = i / fade_n2
        menu_drone[i] *= f
        menu_drone[mn - 1 - i] *= f
    write_wav(menu_drone, "ambient_murder.mp3")

    # ---- victory music: short triumphant progression (one-shot, not looped)
    prog = [392, 523, 659, 784, 659, 784, 988, 1046]
    parts = [_tone(f, 0.28, vol=0.28, attack=0.01, release=0.6) for f in prog]
    chord = _mix(*[_tone(f, 1.0, vol=0.15, attack=0.05, release=1.2) for f in (523, 659, 784)])
    write_wav(_concat_with_gap(*parts, gap=0.02) + chord, "correct.mp3")

    # ---- game over music: somber descending progression (one-shot)
    prog2 = [440, 392, 349, 294, 261]
    parts2 = [_tone(f, 0.4, vol=0.26, wave_type="sine", attack=0.02, release=0.8) for f in prog2]
    low_chord = _mix(*[_tone(f, 1.6, vol=0.14, attack=0.1, release=1.8) for f in (130, 165, 196)])
    write_wav(_concat_with_gap(*parts2, gap=0.04) + low_chord, "gameover_music.wav")


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    make_title_bg()
    make_menu_bg()
    make_case1_bg()
    make_case2_bg()
    make_case3_bg()
    make_case4_bg()
    make_case5_bg()
    make_case6_bg()
    make_case7_bg()
    make_case8_bg()
    make_case9_bg()
    make_case10_bg()
    make_case11_bg()
    make_case12_bg()
    make_case13_bg()
    make_case14_bg()
    make_result_bgs()
    make_avatars()
    make_icon_badge()
    make_icon_magnifier()
    make_sounds()
    print("\nAll assets generated successfully.")
