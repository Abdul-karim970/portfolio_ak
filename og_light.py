#!/usr/bin/env python3
"""Regenerate OG share image (1200x630) in the v3 light-glass style."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
img = Image.new("RGB", (W, H), (238, 242, 250))

# soft mesh blobs (professional blue family)
for (cx, cy, rad, color, alpha) in [
    (1020, 90, 400, (147, 197, 253), 210),
    (1140, 560, 380, (165, 180, 252), 200),
    (120, 600, 360, (129, 140, 248), 140),
]:
    blob = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(blob)
    d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=color + (alpha,))
    blob = blob.filter(ImageFilter.GaussianBlur(150))
    img = Image.alpha_composite(img.convert("RGBA"), blob).convert("RGB")

d = ImageDraw.Draw(img)

def load_font(size, bold=True):
    cands = [
        "/System/Library/Fonts/Supplemental/Arial Black.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

f_name = load_font(58)
f_role = load_font(30)
f_sub = load_font(23, bold=False)

d.text((70, 185), "ABDUL KARIM", font=f_name, fill=(13, 21, 38))
# gradient role pill
pill = Image.new("RGBA", (470, 54), (0, 0, 0, 0))
pd = ImageDraw.Draw(pill)
for x in range(470):
    t = x / 470
    r = int(79 + (67 - 79) * t); g = int(125 + (56 - 125) * t); b = int(243 + (202 - 243) * t)
    pd.line((x, 0, x, 54), fill=(r, g, b, 255))
mask = Image.new("L", (470, 54), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, 470, 54), radius=27, fill=255)
img.paste(pill, (70, 268), mask)
d.text((96, 280), "Senior Flutter Developer", font=f_role, fill=(255, 255, 255))

d.text((70, 366), "AI-Powered App Development  ·  40+ Apps Published", font=f_sub, fill=(63, 74, 99))
d.text((70, 404), "iOS & Android  ·  Clean Architecture  ·  80k+ Downloads", font=f_sub, fill=(114, 122, 153))

# hero cutout right
hero = Image.open("images/opt/hero.webp").convert("RGBA")
cut_h = 560
cut = hero.resize((int(hero.width * cut_h / hero.height), cut_h), Image.LANCZOS)
# soft fade at bottom of cutout
fade = Image.new("L", cut.size, 255)
fd = ImageDraw.Draw(fade)
for y in range(int(cut.height * 0.86), cut.height):
    a = int(255 * (1 - (y - cut.height * 0.86) / (cut.height * 0.14)))
    fd.line((0, y, cut.width, y), fill=a)
cut.putalpha(Image.composite(cut.getchannel("A"), Image.new("L", cut.size, 0), fade))
img.paste(cut, (W - cut.width - 30, H - cut_h + 12), cut)

img.save("images/opt/og-image.jpg", "JPEG", quality=86)
print("og-image.jpg", os.path.getsize("images/opt/og-image.jpg") // 1024, "KB")
