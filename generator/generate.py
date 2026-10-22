#!/usr/bin/env python3
"""
Lil Omnis — trait generation pipeline (v0.1 proof of concept)
Base model: BudE's shadow-being (layers/base/base_body.png)
Chain color schemes + freemasonry-style sigils + mystic backgrounds.

Run:  python3 generate.py
Out:  out/omnis_<chain>.png (1024x1024 each) + out/test_strip.png
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "layers", "base", "base_body.png")
OUT = os.path.join(HERE, "out")

# eye centers measured from the 897px base art
EYES_897 = [(387, 322, 50, 35), (491, 322, 48, 34)]  # cx, cy, w, h

CHAINS = {
    "ETHEREUM":  {"primary": (98, 126, 234), "accent": (200, 215, 255)},
    "BASE":      {"primary": (0, 82, 255),   "accent": (140, 180, 255)},
    "ROBINHOOD": {"primary": (0, 200, 5),    "accent": (150, 255, 150)},
    "SOLANA":    {"primary": (153, 69, 255), "accent": (20, 241, 149)},
    "SUI":       {"primary": (77, 162, 255), "accent": (160, 215, 255)},
    "BIGNETWORK":{"primary": (217, 180, 91), "accent": (242, 234, 214)},
}

GOLD = (217, 180, 91)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def radial_bg(size, color):
    """near-black radial background tinted with the chain color"""
    im = Image.new("RGB", (size, size))
    px = im.load()
    cx = cy = size / 2
    maxd = math.hypot(cx, cy)
    dark = (5, 6, 13)
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy) / maxd
            # tint strongest at center, falls off
            t = max(0.0, 1 - d) ** 1.8 * 0.5
            px[x, y] = lerp(dark, color, t)
    return im


def mystic_ring(size, color, alpha=90):
    """thin double circle + rotated square behind the creature"""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = size // 2
    r1 = int(size * 0.36)
    r2 = int(size * 0.415)
    col = color + (alpha,)
    d.ellipse([c - r1, c - r1, c + r1, c + r1], outline=col, width=3)
    d.ellipse([c - r2, c - r2, c + r2, c + r2], outline=col[:3] + (max(0, alpha-30),), width=1)
    # rotated square inscribed (masonic geometry)
    sq = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sq)
    s = r1 * 1.02
    pts = [(c, c - s), (c + s, c), (c, c + s), (c - s, c)]
    ds.polygon(pts, outline=col, width=2)
    sq = sq.rotate(15, center=(c, c))
    layer = Image.alpha_composite(sq, layer)
    return layer.filter(ImageFilter.GaussianBlur(0.6))


def sigil(kind, size=220, color=GOLD):
    """freemasonry-style chain sigil, drawn in thin strokes"""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size / 2
    col = color + (255,)
    w = 3
    if kind == "ETHEREUM":
        s = size * 0.30
        pts = [(c, c - s), (c + s, c + s * 0.45), (c, c + s), (c - s, c + s * 0.45)]
        d.polygon(pts, outline=col, width=w)
        d.line([(c - s * 0.62, c + s * 0.02), (c, c + s * 0.45), (c + s * 0.62, c + s * 0.02)], fill=col, width=w)
    elif kind == "BASE":
        r = size * 0.32
        d.ellipse([c - r, c - r, c + r, c + r], outline=col, width=w)
        d.line([(c - r, c), (c + r, c)], fill=col, width=w)
    elif kind == "ROBINHOOD":
        s = size * 0.30
        d.line([(c, c + s), (c, c - s)], fill=col, width=w)               # shaft
        d.line([(c - s * 0.45, c + s * 0.2), (c, c - s * 0.15), (c + s * 0.45, c + s * 0.2)], fill=col, width=w)  # head
        d.line([(c - s * 0.4, c - s * 0.55), (c, c - s), (c + s * 0.4, c - s * 0.55)], fill=col, width=w)          # fletch
    elif kind == "BNB":
        s = size * 0.16
        for i, (dx, dy) in enumerate([(0, -1.6), (-1, -0.55), (1, -0.55), (-1, 0.55), (1, 0.55), (0, 1.6)]):
            x, y = c + dx * s, c + dy * s
            d.polygon([(x, y - s), (x + s * 0.8, y), (x, y + s), (x - s * 0.8, y)], outline=col, width=max(2, w - 1))
    elif kind == "SOLANA":
        s = size * 0.28
        for i, dy in enumerate([-1, 0, 1]):
            y = c + dy * s * 0.9
            d.line([(c - s, y + (3 - i) * s * 0.12), (c + s, y + (i - 1) * s * 0.12)], fill=col, width=w)
    elif kind == "SUI":
        r = size * 0.22
        d.ellipse([c - r, c - r * 0.2, c + r, c + r * 1.8], outline=col, width=w)
        d.polygon([(c - r * 0.62, c - r * 0.15), (c, c - size * 0.30), (c + r * 0.62, c - r * 0.15)], outline=col, width=w)
    elif kind == "BIGNETWORK":
        r = size * 0.30
        d.ellipse([c - r, c - r, c + r, c + r], outline=col, width=w)
        dr = size * 0.085
        d.ellipse([c - dr, c - dr, c + dr, c + dr], fill=col)
    return im


def eye_glow(base_size, scale, offset, color, accent):
    """soft glowing eyes at the base art's eye positions, mapped into composition space"""
    layer = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for (cx, cy, w, h) in EYES_897:
        ex = offset[0] + cx * scale
        ey = offset[1] + cy * scale
        rx, ry = w * scale / 2, h * scale / 2
        # outer soft glow
        for i in range(6, 0, -1):
            t = i / 6
            rr = (max(rx, ry) * (0.8 + t * 1.6))
            d.ellipse([ex - rr, ey - rr * 0.8, ex + rr, ey + rr * 0.8], fill=color + (int(14 * (7 - i)),))
        # core
        d.ellipse([ex - rx, ey - ry, ex + rx, ey + ry], fill=accent + (255,))
    return layer.filter(ImageFilter.GaussianBlur(2.2))


def ground_shadow(im, cy, rx, alpha=90):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([512 - rx, cy - 18, 512 + rx, cy + 18], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(im.convert("RGBA"), layer.filter(ImageFilter.GaussianBlur(12))).convert("RGB")



def rim_light(body_img, color):
    """chain-colored rim light along the body silhouette so it reads on dark bg"""
    import numpy as np
    from scipy import ndimage
    a = np.array(body_img)[:, :, 3]
    edge = (a > 100) & ~ndimage.binary_erosion(a > 100, iterations=2)
    layer = np.zeros((a.shape[0], a.shape[1], 4), dtype=np.uint8)
    layer[:, :, 0], layer[:, :, 1], layer[:, :, 2] = color
    layer[:, :, 3] = (edge * 230).astype(np.uint8)
    im = Image.fromarray(layer, "RGBA").filter(ImageFilter.GaussianBlur(1.1))
    halo = im.filter(ImageFilter.GaussianBlur(7))
    halopx = np.array(halo); halopx[:, :, 3] = (halopx[:, :, 3] * 0.45).astype(np.uint8)
    halo = Image.fromarray(halopx, "RGBA")
    return Image.alpha_composite(halo, im)


def render(chain_name, spec):
    size = 1024
    color = spec["primary"]
    accent = spec["accent"]

    canvas = radial_bg(size, color).convert("RGBA")
    canvas = Image.alpha_composite(canvas, mystic_ring(size, color))
    canvas = Image.alpha_composite(canvas, mystic_ring(size, GOLD, alpha=40))

    # body: scale base to ~72% of canvas
    body = Image.open(BASE).convert("RGBA")
    target = int(size * 0.72)
    scale = target / 897
    body = body.resize((target, target), Image.LANCZOS)
    # base cutout canvas is 897 with figure roughly filling it; center it slightly low
    off = ((size - target) // 2, int((size - target) * 0.56))
    canvas.alpha_composite(body, off)
    rl = rim_light(body, color)
    canvas.alpha_composite(rl, off)

    # eye glow
    canvas = Image.alpha_composite(canvas, eye_glow(897, scale, off, color, accent))

    # sigil above the head
    sg = sigil(chain_name, 220, GOLD)
    canvas.alpha_composite(sg, (size // 2 - 110, int(size * 0.055)))

    out = canvas.convert("RGB")

    # ground shadow
    feet_y = int(off[1] + target * 0.965)
    out = ground_shadow(out, feet_y, int(target * 0.30))

    # label
    d = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 30)
    except Exception:
        font = ImageFont.load_default()
    label = chain_name
    tw = d.textlength(label, font=font)
    d.text((size / 2 - tw / 2, size - 74), label, font=font, fill=GOLD)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    panels = []
    for name, spec in CHAINS.items():
        img = render(name, spec)
        img.save(os.path.join(OUT, f"omnis_{name.lower()}.png"))
        panels.append((name, img))
        print("rendered", name)

    # test strip 4x2
    cell = 512
    strip = Image.new("RGB", (cell * 4, cell * 2), (3, 4, 9))
    for i, (name, img) in enumerate(panels):
        r, c = divmod(i, 4)
        strip.paste(img.resize((cell, cell), Image.LANCZOS), (c * cell, r * cell))
    # 8th cell: title block
    d = ImageDraw.Draw(strip)
    try:
        f_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 44)
        f_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 19)
    except Exception:
        f_big = f_small = ImageFont.load_default()
    x0, y0 = cell * 3 + 20, cell + cell // 2 - 40
    d.text((x0, y0), "LIL OMNIS", font=f_big, fill=(242, 234, 214))
    d.text((x0 + 4, y0 + 58), "BASE MODEL: TEST LAYER PASS", font=f_small, fill=(107, 114, 144))
    d.text((x0 + 4, y0 + 86), "EYES / SIGIL / AURA / SHADOW", font=f_small, fill=(107, 114, 144))
    d.text((x0 + 4, y0 + 114), "PIPELINE v0.1", font=f_small, fill=GOLD)
    strip.save(os.path.join(OUT, "test_strip.png"))
    print("saved test_strip.png", strip.size)


if __name__ == "__main__":
    main()
