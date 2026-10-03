#!/usr/bin/env python3
"""Regenerate OG share image (1200x630) — mirrors the site hero (light glass, blue->indigo)."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
F_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
F_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
F_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def hx(h, a=255):
    r, g, b = (int(h[i:i+2], 16) for i in (1, 3, 5))
    return (r, g, b, a)

# ---- background: lavender -> white vertical gradient
img = Image.new("RGB", (1, H))
for y in range(H):
    t = y / H
    img.putpixel((0, y), tuple(int((242, 244, 252)[i] + (255 - (242, 244, 252)[i]) * t) for i in range(3)))
img = img.resize((W, H)).convert("RGBA")

# ---- soft indigo blobs
def blob(cx, cy, r, rgb, alpha):
    b = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgb + (alpha,))
    img.alpha_composite(b.filter(ImageFilter.GaussianBlur(110)))

blob(170, 60, 300, (99, 141, 247), 105)
blob(1060, 120, 250, (129, 140, 248), 85)
blob(1010, 600, 300, (99, 102, 241), 70)

# ---- subtle grid, fading out toward the bottom
grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(grid)
for x in range(0, W, 54):
    gd.line((x, 0, x, H), fill=(16, 20, 43, 11), width=1)
for y in range(0, H, 54):
    gd.line((0, y, W, y), fill=(16, 20, 43, 11), width=1)
gmask = Image.new("L", (W, H), 0)
gm = ImageDraw.Draw(gmask)
for y in range(H):
    gm.line((0, y, W, y), fill=max(0, int(115 * (1 - y / H))))
img = Image.composite(grid, img, gmask)

d = ImageDraw.Draw(img, "RGBA")

# ---- availability pill
f_pill = font(F_BOLD, 19)
txt = "Available for new projects"
tw = d.textlength(txt, font=f_pill)
d.rounded_rectangle((70, 64, 70 + tw + 52, 64 + 42), radius=21,
                    fill=(255, 255, 255, 210), outline=(16, 185, 129, 110), width=1)
d.ellipse((92, 64 + 15, 92 + 10, 64 + 25), fill=(16, 185, 129, 255))
d.text((112, 64 + 10), txt, font=f_pill, fill=(4, 120, 87, 255))

# ---- name
d.text((66, 128), "Abdul Karim", font=font(F_BLACK, 84), fill=(16, 20, 43, 255))

# ---- gradient tagline (blue -> indigo) clipped through text
tag = "AI-Powered App Development"
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).text((70, 246), tag, font=font(F_BOLD, 44), fill=255)
grad = Image.new("RGBA", (W, H))
gg = ImageDraw.Draw(grad)
c1, c2 = (79, 125, 243), (79, 70, 229)
for x in range(W):
    t = x / W
    gg.line((x, 0, x, H), fill=(int(c1[0] + (c2[0] - c1[0]) * t),
                                int(c1[1] + (c2[1] - c1[1]) * t),
                                int(c1[2] + (c2[2] - c1[2]) * t), 255))
img = Image.composite(grad, img, mask)
d = ImageDraw.Draw(img, "RGBA")

# ---- intro copy
f_body = font(F_REG, 22)
lines = [
    "I build and ship production-grade Flutter applications for iOS",
    "and Android — with LLM-powered assistants, AI integrations,",
    "on-device intelligence, and real-time backend systems.",
]
y = 336
for line in lines:
    d.text((70, y), line, font=f_body, fill=(68, 73, 107, 255))
    y += 34

# ---- stats row
f_num = font(F_BLACK, 38)
f_lab = font(F_REG, 14)
stats = [("5+", "YEARS EXPERIENCE", 70), ("40+", "APPS PUBLISHED", 290)]
for num, lab, sx in stats:
    d.text((sx, 470), num, font=f_num, fill=(16, 20, 43, 255))
    d.text((sx + 2, 524), lab, font=f_lab, fill=(117, 123, 153, 255))
d.line((250, 478, 250, 556), fill=(16, 20, 43, 40), width=1)
d.line((470, 478, 470, 556), fill=(16, 20, 43, 40), width=1)

# ---- portrait cutout with glow, faded into the background
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse((760, 130, 1180, 560), fill=(99, 141, 247, 105))
img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))

hero = Image.open("images/opt/hero.webp").convert("RGBA")
ph_h = 560
ph = hero.resize((int(hero.width * ph_h / hero.height), ph_h), Image.LANCZOS)
fade = Image.new("L", ph.size, 255)
fd = ImageDraw.Draw(fade)
for yy in range(int(ph.height * 0.7), ph.height):
    fd.line((0, yy, ph.width, yy), fill=int(255 * (1 - (yy - ph.height * 0.7) / (ph.height * 0.3))))
ph.putalpha(Image.composite(ph.getchannel("A"), Image.new("L", ph.size, 0), fade))
img.alpha_composite(ph, (W - ph.width - 36, H - ph.height - 6))

# ---- bottom-left brand
d.text((70, 588), "abdulkarim-portfolio.netlify.app", font=font(F_REG, 16), fill=(117, 123, 153, 255))

img.convert("RGB").save("images/opt/og-image.jpg", "JPEG", quality=88)
print("og-image.jpg", os.path.getsize("images/opt/og-image.jpg") // 1024, "KB")
