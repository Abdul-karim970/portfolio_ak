#!/usr/bin/env python3
"""
Showcase compositor: builds light, readable, per-project showcase images from
the real app screenshots in images/ss/. Each project gets its own layout style;
featured projects (clust, flynet, safrly) get 3 slides each for carousels.

Output: images/showcase/<slug>_s<n>.webp  (1600x1000, q82)
"""
import os
import glob as _glob
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1600, 1000
SS = "images/ss"
OUT = "images/showcase"
os.makedirs(OUT, exist_ok=True)

def G(pattern, count=None):
    """glob-resolve screenshot files (macOS names may contain odd spaces)"""
    hits = sorted(_glob.glob(pattern))
    return hits[:count] if count else hits

F_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
F_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
F_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def hx(c, a=255):
    r, g, b = (int(c[i:i+2], 16) for i in (1, 3, 5))
    return (r, g, b, a)

def mix_white(c_hex, ratio):
    """accent color blended toward white (for pills/tints on light bg)"""
    r, g, b = (int(c_hex[i:i+2], 16) for i in (1, 3, 5))
    return (int(r + (255 - r) * ratio), int(g + (255 - g) * ratio), int(b + (255 - b) * ratio))

# ---------------------------------------------------------------- backgrounds
def gradient_bg(tint_hex):
    top = mix_white(tint_hex, 0.82)
    bottom = (255, 255, 255)
    base = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / H
        base.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return base.resize((W, H))

def blob(layer, cx, cy, r, accent_hex, alpha):
    b = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=hx(accent_hex, alpha))
    b = b.filter(ImageFilter.GaussianBlur(140))
    layer.alpha_composite(b)

def overlay(layer, fn):
    """draw semi-transparent decoration on a transparent tile, then composite"""
    ov = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(ov))
    layer.alpha_composite(ov)

def dots_motif(layer, accent_hex, x0, y0, cols, rows, step=34, alpha=26, r=3):
    def draw(d):
        for i in range(cols):
            for j in range(rows):
                x, y = x0 + i * step, y0 + j * step
                d.ellipse((x - r, y - r, x + r, y + r), fill=hx(accent_hex, alpha))
    overlay(layer, draw)

def rings_motif(layer, accent_hex, cx, cy, radii, alpha=22, width=2):
    def draw(d):
        for r in radii:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=hx(accent_hex, alpha), width=width)
    overlay(layer, draw)

def bands_motif(layer, accent_hex, alpha=14):
    b = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    for x, w in [(-200, 240), (300, 160), (900, 300), (1380, 220)]:
        d.rectangle((x, -200, x + w, H + 200), fill=hx(accent_hex, alpha))
    b = b.rotate(18, expand=False, resample=Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
    layer.alpha_composite(b)

def watermark(layer, word, accent_hex, alpha=13, size=250, y=None):
    d0 = ImageDraw.Draw(layer)
    while size > 60 and d0.textlength(word, font=font(F_BLACK, size)) > W - 90:
        size -= 10
    f = font(F_BLACK, size)
    tw = d0.textlength(word, font=f)
    x = W - tw - 40
    yy = H - size - 30 if y is None else y
    def draw(d):
        d.text((x, yy), word, font=f, fill=hx(accent_hex, alpha))
    overlay(layer, draw)

# ---------------------------------------------------------------- components
def cover(img, w, h):
    s = max(w / img.width, h / img.height)
    im = img.resize((int(img.width * s + 0.5), int(img.height * s + 0.5)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def rounded_shadow_box(img, w, radius, bezel=0, bezel_color=(13, 18, 32, 255),
                       rot=0, shadow_alpha=95, sharpen=True, screen_ratio=None):
    """img -> RGBA with rounded corners (+optional bezel), drop shadow, optional rotation."""
    if screen_ratio:  # force aspect (w/h) for store cards
        h = int(w / screen_ratio)
    else:
        h = int(round(w * img.height / img.width))
    im = cover(img, w, h)
    if sharpen:
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    # rounded screen
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    screen = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    screen.paste(im.convert("RGBA"), (0, 0), mask)

    if bezel:
        pad = bezel
        outer_w, outer_h = w + pad * 2, h + pad * 2
        body = Image.new("RGBA", (outer_w, outer_h), (0, 0, 0, 0))
        bd = ImageDraw.Draw(body)
        bd.rounded_rectangle((0, 0, outer_w, outer_h), radius=radius + pad, fill=bezel_color)
        bd.rounded_rectangle((pad - 1, pad - 1, pad + w + 1, pad + h + 1), radius=radius,
                             outline=(255, 255, 255, 40), width=1)
        body.paste(screen, (pad, pad), screen)
        card = body
    else:
        card = screen

    if rot:
        card = card.rotate(rot, expand=True, resample=Image.BICUBIC)

    # drop shadow
    m = 90
    sh = Image.new("RGBA", (card.width + m * 2, card.height + m * 2), (0, 0, 0, 0))
    sh_mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(sh_mask).rounded_rectangle((0, 0, card.width, card.height),
                                              radius=radius + bezel, fill=shadow_alpha)
    sh.paste((10, 16, 30, shadow_alpha), (m, m), sh_mask)
    sh = sh.filter(ImageFilter.GaussianBlur(26))
    sh.alpha_composite(card, (m, m))
    return sh

def phone(screen_img, screen_w, rot=0, bezel=11):
    return rounded_shadow_box(screen_img, screen_w, radius=int(screen_w * 0.135),
                              bezel=bezel, rot=rot)

def paste_center(canvas, card, cx, cy):
    canvas.alpha_composite(card, (int(cx - card.width / 2), int(cy - card.height / 2)))

# ---------------------------------------------------------------- text block
def text_block(layer, x, y, accent_hex, kicker, title, tagline=None, pill_text=None,
               align="left", title_size=86, max_tag_w=600, dark=(14, 21, 38)):
    d = ImageDraw.Draw(layer, "RGBA")
    f_kick = font(F_BOLD, 25)
    f_title = font(F_BLACK, title_size)
    f_tag = font(F_REG, 33)
    f_pill = font(F_BOLD, 26)

    def center_x(text, f, box_x, box_w):
        return box_x + (box_w - d.textlength(text, font=f)) / 2

    if align == "center":
        cx0, cw = 0, W
        d.text((center_x(kicker, f_kick, cx0, cw), y), kicker, font=f_kick, fill=hx(accent_hex))
        y += 46
        d.text((center_x(title, f_title, cx0, cw), y), title, font=f_title, fill=dark)
        y += title_size + 22
        if tagline:
            for line in wrap(tagline, f_tag, 760):
                d.text((center_x(line, f_tag, cx0, cw), y), line, font=f_tag, fill=(91, 100, 120))
                y += 46
            y += 26
        if pill_text:
            pw = d.textlength(pill_text, font=f_pill) + 76
            px = (W - pw) / 2
            def draw(d):
                d.rounded_rectangle((px, y, px + pw, y + 56), radius=28,
                                    fill=hx(accent_hex, 36), outline=hx(accent_hex, 90), width=2)
                d.text((px + 38, y + 13), pill_text, font=f_pill, fill=hx(accent_hex))
            overlay(layer, draw)
        return

    d.text((x, y), kicker, font=f_kick, fill=hx(accent_hex))
    y += 48
    for line in wrap(title, f_title, max_tag_w):
        d.text((x, y), line, font=f_title, fill=dark)
        y += title_size + 10
    y += 14
    if tagline:
        for line in wrap(tagline, f_tag, max_tag_w):
            d.text((x, y), line, font=f_tag, fill=(91, 100, 120))
            y += 46
        y += 30
    if pill_text:
        pw = d.textlength(pill_text, font=f_pill) + 76
        def draw(d):
            d.rounded_rectangle((x, y, x + pw, y + 56), radius=28,
                                fill=hx(accent_hex, 36), outline=hx(accent_hex, 90), width=2)
            d.text((x + 38, y + 13), pill_text, font=f_pill, fill=hx(accent_hex))
        overlay(layer, draw)

def wrap(text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if ImageDraw.Draw(Image.new("RGB", (10, 10))).textlength(t, font=f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- styles
def style_split(cfg, canvas, side="right", phone_w=370, rot=0, duo=False, ss_idx=(0, 1)):
    """text on one side, phone(s) on the other"""
    a = cfg["accent"]
    if side == "right":
        blob(canvas, W - 160, H * 0.42, 430, a, 34)
        dots_motif(canvas, a, 84, H - 200, 6, 4)
        text_block(canvas, 96, 150, a, cfg["kicker"], cfg["title"], cfg["tagline"], cfg["metric"],
                   max_tag_w=620)
        img1 = load_img(cfg["ss"][ss_idx[0]])
        p1 = phone(img1, phone_w, rot=rot)
        if duo and len(cfg["ss"]) > ss_idx[1]:
            p2 = phone(load_img(cfg["ss"][ss_idx[1]]), int(phone_w * 0.82), rot=-rot - 4)
            paste_center(canvas, p2, W - 285, H * 0.62)
            paste_center(canvas, p1, W - 565, H * 0.46)
        else:
            paste_center(canvas, p1, W - 350, H * 0.52)
    else:
        blob(canvas, 200, H * 0.5, 430, a, 34)
        dots_motif(canvas, a, W - 300, 90, 6, 4)
        text_block(canvas, W - 760, 170, a, cfg["kicker"], cfg["title"], cfg["tagline"], cfg["metric"],
                   max_tag_w=620)
        img1 = load_img(cfg["ss"][ss_idx[0]])
        p1 = phone(img1, phone_w, rot=rot)
        if duo and len(cfg["ss"]) > ss_idx[1]:
            p2 = phone(load_img(cfg["ss"][ss_idx[1]]), int(phone_w * 0.82), rot=rot + 5)
            paste_center(canvas, p2, 285, H * 0.62)
            paste_center(canvas, p1, 565, H * 0.46)
        else:
            paste_center(canvas, p1, 360, H * 0.52)

def style_hero_center(cfg, canvas, phone_w=306, card=False):
    a = cfg["accent"]
    blob(canvas, W / 2, -120, 520, a, 30)
    blob(canvas, 120, H + 60, 380, a, 24)
    rings_motif(canvas, a, W - 170, 170, [70, 120, 170], alpha=20)
    text_block(canvas, 0, 92, a, cfg["kicker"], cfg["title"], cfg["tagline"], cfg["metric"],
               align="center", title_size=84)
    img = load_img(cfg["ss"][0])
    if card:
        p = rounded_shadow_box(img, 360, radius=34, screen_ratio=0.5)
    else:
        p = phone(img, phone_w)
    top_y = 540
    paste_center(canvas, p, W / 2, top_y + p.height / 2 - 70)

def style_stat(cfg, canvas, phone_w=360, bubble_text=None, bubble_label=None, side="left"):
    a = cfg["accent"]
    if side == "left":
        blob(canvas, 190, H * 0.5, 420, a, 34)
        text_block(canvas, W - 750, 200, a, cfg["kicker"], cfg["title"], cfg["tagline"], None,
                   max_tag_w=600)
        p = phone(load_img(cfg["ss"][0]), phone_w, rot=-3)
        paste_center(canvas, p, 420, H * 0.55)
    else:
        blob(canvas, W - 200, H * 0.5, 420, a, 34)
        text_block(canvas, 96, 200, a, cfg["kicker"], cfg["title"], cfg["tagline"], None,
                   max_tag_w=600)
        p = phone(load_img(cfg["ss"][0]), phone_w, rot=3)
        paste_center(canvas, p, W - 420, H * 0.55)
    # floating metric bubble — anchored over the phone's top corner, clear of text
    f_big = font(F_BLACK, 58)
    f_lab = font(F_BOLD, 22)
    d = ImageDraw.Draw(canvas)
    bt = bubble_text or cfg["metric"]
    bw = max(d.textlength(bt, font=f_big), d.textlength(bubble_label or "", font=f_lab)) + 90
    if side == "left":
        bx = 660 - int(bw / 2)
    else:
        bx = W - 660 - int(bw / 2)
    by = 78
    bubble = Image.new("RGBA", (int(bw), 168), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bubble)
    bd.rounded_rectangle((0, 0, bubble.width, 168), radius=36, fill=hx(a, 235),
                         outline=(255, 255, 255, 120), width=2)
    bd.text(((bubble.width - d.textlength(bt, font=f_big)) / 2, 30), bt, font=f_big, fill=(255, 255, 255, 255))
    if bubble_label:
        bd.text(((bubble.width - d.textlength(bubble_label, font=f_lab)) / 2, 106), bubble_label,
                font=f_lab, fill=(255, 255, 255, 210))
    sh = Image.new("RGBA", (bubble.width + 80, 248), (0, 0, 0, 0))
    shm = Image.new("L", bubble.size, 0)
    ImageDraw.Draw(shm).rounded_rectangle((0, 0, bubble.width, 168), radius=36, fill=110)
    sh.paste((10, 16, 30, 110), (40, 40), shm)
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    sh.alpha_composite(bubble, (40, 40))
    canvas.alpha_composite(sh, (bx - 40, by - 40))

def style_diagonal(cfg, canvas, phone_w=380, rot=8):
    a = cfg["accent"]
    bands_motif(canvas, a)
    watermark(canvas, cfg["title"].split(" ")[0].upper(), a, alpha=15, size=230)
    text_block(canvas, 96, 210, a, cfg["kicker"], cfg["title"], cfg["tagline"], cfg["metric"],
               max_tag_w=580)
    p = phone(load_img(cfg["ss"][0]), phone_w, rot=rot)
    paste_center(canvas, p, W - 400, H * 0.55)

def style_banner_card(cfg, canvas):
    """for projects without raw screens — existing banner in a rounded dark card"""
    a = cfg["accent"]
    blob(canvas, W - 200, H * 0.4, 420, a, 30)
    dots_motif(canvas, a, 96, 110, 5, 4)
    text_block(canvas, 96, 210, a, cfg["kicker"], cfg["title"], cfg["tagline"], cfg["metric"],
               max_tag_w=520)
    img = load_img(cfg["ss"][0])
    card = rounded_shadow_box(img, 760, radius=30, screen_ratio=1.35)
    paste_center(canvas, card, W - 520, H * 0.54)

def load_img(path):
    im = Image.open(path)
    return im.convert("RGB") if im.mode != "RGBA" else im

def render(cfg, style, out_name):
    canvas = gradient_bg(cfg["tint"]).convert("RGBA")
    style(cfg, canvas)
    canvas.convert("RGB").save(f"{OUT}/{out_name}.webp", "WEBP", quality=82, method=6)
    print(f"  {out_name}.webp")

# ---------------------------------------------------------------- configs
def S(folder, names):
    return [os.path.join(SS, folder, n) for n in names]

PROJECTS = [
    dict(slug="clodoc", accent="#0d9488", tint="#f0fdfa", kicker="TELEMEDICINE",
         title="Clodocs", tagline="Secure video consultations with appointment booking and visit history.",
         metric="Agora RTC", ss=S("clodoc", ["1.webp", "2.webp", "3.webp", "4.webp"])),
    dict(slug="comp", accent="#1e3a8a", tint="#eff6ff", kicker="WORKFORCE ENTERPRISE",
         title="iClock Company", tagline="Shift planning, attendance exceptions and presence analytics for teams.",
         metric="Admin console", ss=S("comp", ["1.webp", "2.webp", "3.webp", "4.webp"])),
    dict(slug="iclock", accent="#0891b2", tint="#ecfeff", kicker="PRODUCTIVITY",
         title="iClock", tagline="Location-verified attendance and paperless leave requests.",
         metric="GPS check-in", ss=S("inviter/iclock", ["1.webp", "2.webp", "3.webp", "4.webp"])),
    dict(slug="inviter", accent="#e11d48", tint="#fff1f2", kicker="EVENTS",
         title="Invitor", tagline="Animated digital invitation cards for every celebration.",
         metric="Creative templates", ss=S("inviter", ["1.webp", "2.webp", "3.webp", "4.webp"])),
    dict(slug="kitchen", accent="#ea580c", tint="#fff7ed", kicker="FOOD DELIVERY",
         title="Mehar's Kitchen", tagline="Menus, quick checkout and real-time delivery tracking.",
         metric="Dubai-based brand", ss=S("kitchen", ["1.webp", "2.webp", "3.webp", "4.webp"])),
    dict(slug="kollysm", accent="#059669", tint="#ecfdf5", kicker="E-COMMERCE",
         title="KollySM", tagline="Catalogs, flash deals, secure checkout and live order tracking.",
         metric="Multi-vendor", ss=S("kollysm", ["1.webp", "4.webp", "2.webp", "3.webp"])),
    dict(slug="moov", accent="#9333ea", tint="#faf5ff", kicker="COACHING & LEARNING",
         title="MOOV Forward", tagline="Private coaches and tutors, booked and paid in the app.",
         metric="Instant booking", ss=S("moov", ["1.webp", "2.webp", "3.webp", "4.webp"])),
    dict(slug="pos", accent="#16a34a", tint="#f0fdf4", kicker="RETAIL",
         title="Codepul POS", tagline="Fast counter billing with live stock updates and sales analytics.",
         metric="Point of Sale", ss=S("pos ", ["WhatsApp Image 2026-02-20 at 21.32.54 (1).jpeg",
                                              "WhatsApp Image 2026-02-20 at 21.32.55 (1).jpeg"])),
    dict(slug="chat", accent="#2563eb", tint="#eff6ff", kicker="MESSAGING",
         title="Messages", tagline="Default SMS messenger with dual-SIM, pinned chats and themes.",
         metric="Dual-SIM", ss=G("images/ss/chat/*.png", 2)),
    dict(slug="sw_dri", accent="#0f766e", tint="#f0fdfa", kicker="DELIVERY",
         title="Sweeft Driver", tagline="Assignments, navigation and clean delivery completion.",
         metric="Field operations", ss=S("sw_dri", ["1.webp", "2.webp", "3.webp"])),
    dict(slug="sweeft_cus", accent="#1d4ed8", tint="#eff6ff", kicker="MARKETPLACE",
         title="Sweeft Customer", tagline="Multi-vendor bookings, orders and real-time tracking.",
         metric="One account", ss=S("sweeft cus", ["1.webp", "2.webp", "3.webp", "4.webp"])),
    dict(slug="thardi_user", accent="#d97706", tint="#fffbeb", kicker="LOGISTICS",
         title="Thardi User", tagline="Book the right cargo vehicle and track shipments to delivery.",
         metric="Real-time tracking", ss=S("thardi/thardi_user", ["thardi user .jpeg", "unnamed (1).jpeg", "unnamed (2).jpeg"])),
    dict(slug="thardi_driver", accent="#475569", tint="#f8fafc", kicker="LOGISTICS",
         title="Thardi Driver", tagline="Accept bookings, manage trips and grow vehicle utilization.",
         metric="Fleet partners", ss=S("thardi/thardi_driver", ["unnamed.jpeg", "unnamed (1).jpeg", "unnamed (2).jpeg"])),
    dict(slug="elms", accent="#7c3aed", tint="#f5f3ff", kicker="EDTECH",
         title="CAS ELMS", tagline="Quizzes, results and geofenced auto-attendance for campus life.",
         metric="Geofencing", ss=S("elms", ["1.webp", "2.webp", "3.webp"])),
    dict(slug="filao", accent="#4f46e5", tint="#eef2ff", kicker="BUSINESS CRM",
         title="Fillao", tagline="Customers, projects, invoices and payments in one workspace.",
         metric="CRM + invoicing", ss=S("filao", ["1.webp", "2.webp", "3.webp", "4.webp"])),
]

# style assignments — every project a different look
ASSIGN = {
    "clodoc":        ("split", dict(side="left", phone_w=370, rot=4)),
    "comp":          ("stat",  dict(side="right", bubble_label="for organizations")),
    "iclock":        ("split", dict(side="right", phone_w=372, rot=-4)),
    "inviter":       ("diagonal", dict(rot=9)),
    "kitchen":       ("hero_center", dict(phone_w=384)),
    "kollysm":       ("split", dict(side="right", phone_w=372, rot=-3, duo=True)),
    "moov":          ("stat",  dict(side="left", bubble_label="coaches & tutors")),
    "pos":           ("split", dict(side="right", phone_w=372, rot=3)),
    "chat":          ("diagonal", dict(rot=-8)),
    "sw_dri":        ("split", dict(side="left", phone_w=368, rot=-3)),
    "sweeft_cus":    ("hero_center", dict(phone_w=380)),
    "thardi_user":   ("stat",  dict(side="left", bubble_label="cargo bookings")),
    "thardi_driver": ("split", dict(side="right", phone_w=370, rot=-4)),
    "elms":          ("split", dict(side="left", phone_w=340, rot=4)),
    "filao":         ("diagonal", dict(rot=-7)),
}

print("Single showcases:")
for cfg in PROJECTS:
    style_name, kw = ASSIGN[cfg["slug"]]
    fn = {"split": style_split, "hero_center": style_hero_center,
          "stat": style_stat, "diagonal": style_diagonal}[style_name]
    render(cfg, fn, cfg["slug"] + "_s1")

# arrow flow — no raw screens, use existing banner
print("Fallback banner card:")
af = dict(slug="arrow_flow", accent="#7c3aed", tint="#f5f3ff", kicker="MOBILE GAME",
          title="Arrow Flow", tagline="Original grid puzzle — 200 levels, stars, lives and rewarded ads.",
          metric="Built with Flame", ss=["images/opt/arrow_flow.webp"])
render(af, style_banner_card, "arrow_flow_s1")

# ---------------------------------------------------------------- featured slides
print("Featured slides:")

clust_cus = dict(accent="#2563eb", tint="#eef4ff", kicker="RIDE-HAILING · ALBANIA · CUSTOMER APP",
                 title="Clust Customer", tagline="One-tap booking, fare estimates, live driver tracking and in-app chat.",
                 metric="10k+ downloads")
clust_dri = dict(accent="#1d4ed8", tint="#eef2ff", kicker="RIDE-HAILING · ALBANIA · DRIVER APP",
                 title="Clust Driver", tagline="Go online, receive rides, navigate trips and track daily earnings.",
                 metric="1k+ downloads")

# slide 1: customer store card right / text left
c1 = gradient_bg(clust_cus["tint"]).convert("RGBA")
blob(c1, W - 180, H * 0.4, 430, clust_cus["accent"], 34)
dots_motif(c1, clust_cus["accent"], 90, H - 190, 6, 4)
text_block(c1, 96, 190, clust_cus["accent"], clust_cus["kicker"], clust_cus["title"],
           clust_cus["tagline"], clust_cus["metric"], max_tag_w=640)
card = rounded_shadow_box(load_img("images/ss/clust user/2.webp"), 420, radius=40, screen_ratio=0.462)
paste_center(c1, card, W - 370, H * 0.52)
c1.convert("RGB").save(f"{OUT}/clust_s1.webp", "WEBP", quality=82, method=6)
print("  clust_s1.webp")

# slide 2: driver store card left / text right
c2 = gradient_bg(clust_dri["tint"]).convert("RGBA")
blob(c2, 190, H * 0.45, 430, clust_dri["accent"], 34)
rings_motif(c2, clust_dri["accent"], W - 180, 160, [60, 110, 160], alpha=20)
text_block(c2, W - 760, 190, clust_dri["accent"], clust_dri["kicker"], clust_dri["title"],
           clust_dri["tagline"], clust_dri["metric"], max_tag_w=640)
card = rounded_shadow_box(load_img("images/ss/clust driver/2.webp"), 420, radius=40, screen_ratio=0.462)
paste_center(c2, card, 370, H * 0.52)
c2.convert("RGB").save(f"{OUT}/clust_s2.webp", "WEBP", quality=82, method=6)
print("  clust_s2.webp")

# slide 3: duo — customer tracking + driver screens
c3 = gradient_bg("#eef4ff").convert("RGBA")
bands_motif(c3, "#2563eb", alpha=12)
text_block(c3, 96, 130, "#2563eb", "RIDE-HAILING · ALBANIA", "Two apps. One platform.",
           "Customer and driver sides working together in real time.", None, max_tag_w=700, title_size=74)
pc = rounded_shadow_box(load_img("images/ss/clust user/5.webp"), 350, radius=34, screen_ratio=0.462, rot=3)
pd = rounded_shadow_box(load_img("images/ss/clust driver/5.webp"), 350, radius=34, screen_ratio=0.462, rot=-4)
paste_center(c3, pc, W - 620, H * 0.60)
paste_center(c3, pd, W - 330, H * 0.56)
c3.convert("RGB").save(f"{OUT}/clust_s3.webp", "WEBP", quality=82, method=6)
print("  clust_s3.webp")

fly = dict(accent="#0e7490", tint="#ecfeff", kicker="ENTERPRISE SECURITY",
           title="Flynet Security", tagline="CCTV monitoring with live streams, cloud recording and incident playback.",
           metric="24/7 surveillance")

f1 = gradient_bg(fly["tint"]).convert("RGBA")
blob(f1, W - 170, H * 0.45, 420, fly["accent"], 34)
dots_motif(f1, fly["accent"], 90, 100, 6, 4)
text_block(f1, 96, 200, fly["accent"], fly["kicker"], fly["title"], fly["tagline"], fly["metric"], max_tag_w=640)
p = phone(load_img("images/ss/flynet/1.webp"), 372, rot=-3)
paste_center(f1, p, W - 360, H * 0.53)
f1.convert("RGB").save(f"{OUT}/flynet_s1.webp", "WEBP", quality=82, method=6)
print("  flynet_s1.webp")

f2 = gradient_bg(fly["tint"]).convert("RGBA")
style_stat(dict(fly, ss=G("images/ss/flynet/*.webp")), f2, side="right", phone_w=368,
           bubble_text="24/7", bubble_label="live monitoring")
f2.convert("RGB").save(f"{OUT}/flynet_s2.webp", "WEBP", quality=82, method=6)
print("  flynet_s2.webp")

f3 = gradient_bg("#ecfeff").convert("RGBA")
rings_motif(f3, fly["accent"], 170, H - 140, [70, 120, 170], alpha=18)
text_block(f3, 96, 130, fly["accent"], "ENTERPRISE CCTV", "Every camera. One app.",
           "Live view, recordings and incident review across supported camera brands.",
           None, max_tag_w=700, title_size=74)
p1 = phone(load_img("images/ss/flynet/2.webp"), 340, rot=3)
p2 = phone(load_img("images/ss/flynet/3.webp"), 340, rot=-5)
paste_center(f3, p2, W - 330, H * 0.58)
paste_center(f3, p1, W - 640, H * 0.54)
f3.convert("RGB").save(f"{OUT}/flynet_s3.webp", "WEBP", quality=82, method=6)
print("  flynet_s3.webp")

saf_par = dict(accent="#0284c7", tint="#f0f9ff", kicker="SCHOOL TRANSPORT · SAUDI ARABIA · PARENT",
               title="Safrly Parent", tagline="Live bus status, boarding alerts and bilingual Arabic/English UX.",
               metric="Live tracking")
saf_dri = dict(accent="#0369a1", tint="#f0f9ff", kicker="SCHOOL TRANSPORT · SAUDI ARABIA · DRIVER",
               title="Safrly Driver", tagline="Rosters, route maps and boarding confirmations every school day.",
               metric="Route control")

s1 = gradient_bg(saf_par["tint"]).convert("RGBA")
blob(s1, W - 180, H * 0.42, 430, saf_par["accent"], 34)
dots_motif(s1, saf_par["accent"], 90, H - 190, 6, 4)
text_block(s1, 96, 190, saf_par["accent"], saf_par["kicker"], saf_par["title"],
           saf_par["tagline"], saf_par["metric"], max_tag_w=640)
p = phone(load_img("images/ss/safrly/parent/unnamed.jpeg"), 380, rot=-3)
paste_center(s1, p, W - 370, H * 0.53)
s1.convert("RGB").save(f"{OUT}/safrly_s1.webp", "WEBP", quality=82, method=6)
print("  safrly_s1.webp")

s2 = gradient_bg(saf_dri["tint"]).convert("RGBA")
blob(s2, 190, H * 0.45, 430, saf_dri["accent"], 34)
rings_motif(s2, saf_dri["accent"], W - 170, 150, [60, 110, 160], alpha=20)
text_block(s2, W - 780, 190, saf_dri["accent"], saf_dri["kicker"], saf_dri["title"],
           saf_dri["tagline"], saf_dri["metric"], max_tag_w=620)
p = phone(load_img("images/ss/safrly/driver/unnamed.jpeg"), 380, rot=3)
paste_center(s2, p, 370, H * 0.53)
s2.convert("RGB").save(f"{OUT}/safrly_s2.webp", "WEBP", quality=82, method=6)
print("  safrly_s2.webp")

s3 = gradient_bg("#f0f9ff").convert("RGBA")
bands_motif(s3, "#0284c7", alpha=12)
text_block(s3, 96, 130, "#0284c7", "SAFRILY PLATFORM", "Parents and drivers, in sync.",
           "One platform connecting families, drivers and admins with real-time trip updates.",
           None, max_tag_w=700, title_size=74)
pp = phone(load_img("images/ss/safrly/parent/unnamed (2).jpeg"), 350, rot=3)
pd2 = phone(load_img("images/ss/safrly/driver/unnamed (2).jpeg"), 350, rot=-5)
paste_center(s3, pd2, W - 330, H * 0.58)
paste_center(s3, pp, W - 640, H * 0.54)
s3.convert("RGB").save(f"{OUT}/safrly_s3.webp", "WEBP", quality=82, method=6)
print("  safrly_s3.webp")

print("\nDone.")
