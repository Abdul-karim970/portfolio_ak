#!/usr/bin/env python3
"""One-off optimizer: convert portfolio images to WebP + build OG share image."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = "images"
OUT = "images/opt"
os.makedirs(OUT, exist_ok=True)

PROJECT_PNGS = [
    "arrow_flow", "clodoc", "clust_customer", "clust_driver", "elms", "Filao",
    "Flynet_security", "iclock", "iclock_compay", "inviter", "kollysm",
    "mehar", "messages", "moov", "pos", "safrly_driver", "safrly_parent",
    "sweeft_driver", "sweeft_store", "sweeft_user", "thardi_driver", "thardi_user",
]

def save_webp(im, path, quality=80):
    im.save(path, "WEBP", quality=quality, method=6)
    kb = os.path.getsize(path) // 1024
    print(f"  {path}  {im.size[0]}x{im.size[1]}  {kb}KB")

# ---- Hero cutout (transparent) ----
hero = Image.open(f"{SRC}/image.png").convert("RGBA")
bbox = hero.getbbox()
pad = 12
l, t, r, b = bbox
l = max(0, l - pad); t = max(0, t - pad)
r = min(hero.width, r + pad); b = min(hero.height, b + pad)
hero = hero.crop((l, t, r, b))
target_h = 1000
hero = hero.resize((int(hero.width * target_h / hero.height), target_h), Image.LANCZOS)
save_webp(hero, f"{OUT}/hero.webp", quality=88)

# ---- About portrait ----
about = Image.open(f"{SRC}/image_flip.jpeg").convert("RGB")
about.thumbnail((640, 640), Image.LANCZOS)
save_webp(about, f"{OUT}/about.webp", quality=82)

# ---- Project banners ----
total_before = total_after = 0
for name in PROJECT_PNGS:
    im = Image.open(f"{SRC}/{name}.png").convert("RGB")
    before = os.path.getsize(f"{SRC}/{name}.png")
    if im.width > 1100:
        im = im.resize((1100, int(im.height * 1100 / im.width)), Image.LANCZOS)
    total_before += before
    save_webp(im, f"{OUT}/{name}.webp", quality=80)
    total_after += os.path.getsize(f"{OUT}/{name}.webp")

print(f"\nBanners: {total_before//1024}KB -> {total_after//1024}KB")

# ---- OG share image 1200x630 ----
W, H = 1200, 630
og = Image.new("RGB", (W, H), (7, 11, 20))
d = ImageDraw.Draw(og)
# aurora blobs
for (cx, cy, rad, color) in [
    (950, 80, 420, (34, 211, 238)), (1120, 560, 420, (139, 92, 246)), (150, 600, 380, (20, 120, 190)),
]:
    blob = Image.new("RGB", (W, H), (0, 0, 0))
    bd = ImageDraw.Draw(blob)
    bd.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=color)
    blob = blob.filter(ImageFilter.GaussianBlur(160))
    og = Image.blend(og, Image.blend(og, blob, 0.5), 0.55) if False else Image.blend(og, blob, 0.18)
d = ImageDraw.Draw(og)

def load_font(size, bold=True):
    cands = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()

f_name = load_font(64)
f_role = load_font(34)
f_sub = load_font(24, bold=False)

d.text((70, 190), "ABDUL KARIM", font=f_name, fill=(245, 248, 255))
d.rounded_rectangle((70, 280, 596, 332), radius=26, fill=(24, 40, 66))
d.text((94, 292), "Senior Flutter Developer", font=f_role, fill=(103, 232, 249))
d.text((70, 372), "AI-Integrated Mobile Apps  •  40+ Apps Published", font=f_sub, fill=(168, 182, 205))
d.text((70, 412), "iOS & Android  •  Clean Architecture  •  5+ Years", font=f_sub, fill=(120, 134, 158))

# hero cutout on the right
cut = hero.copy()
cut_h = 560
cut = cut.resize((int(cut.width * cut_h / cut.height), cut_h), Image.LANCZOS)
og.paste(cut, (W - cut.width - 40, H - cut_h + 10), cut)

og.save(f"{OUT}/og-image.jpg", "JPEG", quality=85)
print(f"  {OUT}/og-image.jpg  {og.size[0]}x{og.size[1]}  {os.path.getsize(f'{OUT}/og-image.jpg')//1024}KB")
print("Done.")
