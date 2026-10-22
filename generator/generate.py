#!/usr/bin/env python3
"""
Lil Omnis — trait generation pipeline (v0.3)
Base model: BudE's shadow-being (layers/base/base_body.png)
Layers: chamber bg -> mystic ring -> vestment (rare) -> body -> rim light ->
        eye glow -> chest sigil -> relic staff + crystal -> ground shadow
Wardens concept: relic staffs with realm crystals (BudE's wardens sheet).

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
    "BNB":       {"primary": (240, 185, 11), "accent": (255, 230, 150)},
    "SOLANA":    {"primary": (153, 69, 255), "accent": (20, 241, 149)},
    "SUI":       {"primary": (77, 162, 255), "accent": (160, 215, 255)},
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
            t = max(0.0, 1 - d) ** 1.8 * 0.34
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


def put_alpha(img, a):
    px = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, al = px[x, y]
            if al: px[x, y] = (r, g, b, a)


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


def flat_chamber(size, color):
    """plain near-black chamber: subtle vertical depth + faint realm floor glow, no symbols"""
    import numpy as np
    a = np.zeros((size, size, 3), dtype=np.uint8)
    top, bot = np.array([4, 5, 11]), np.array([9, 11, 20])
    for y in range(size):
        a[y, :, :] = (top + (bot - top) * (y / size)).astype(np.uint8)
    im = Image.fromarray(a, "RGB").convert("RGBA")
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    d.ellipse([size * 0.18, size * 0.80, size * 0.82, size * 1.06], fill=color + (46,))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    return Image.alpha_composite(im, glow)


def robe_pattern(body_img, chain_name, color, strength=80):
    """embroidered realm motif: small sigils woven in a diamond grid over the robe"""
    import numpy as np
    w, h = body_img.size
    tile = sigil(chain_name, 58, tuple(min(255, int(v * 1.35)) for v in color))
    put_alpha(tile, strength)
    tw = 88
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    robe_top = int(h * 0.42)
    row = 0
    for y in range(robe_top, h, tw):
        shift = (tw // 2) if row % 2 else 0
        for x in range(-tw, w, tw):
            layer.alpha_composite(tile, (x + shift, y))
        row += 1
    # clip to body silhouette
    la = np.array(layer); la[:, :, 3] = np.minimum(la[:, :, 3], np.array(body_img)[:, :, 3])
    return Image.alpha_composite(body_img, Image.fromarray(la, "RGBA"))


def amulet(chain_name, color, accent, off, scale, size=110):
    """the realm mark worn as an accessory: sigil pendant on a thin cord"""
    layer = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = off[0] + int(440 * scale)
    cy = off[1] + int(490 * scale)
    # cord: V lines from shoulders to pendant
    cord = (150, 128, 74, 200)
    d.line([(cx - int(150 * scale), cy - int(150 * scale)), (cx, cy - 30)], fill=cord, width=3)
    d.line([(cx + int(150 * scale), cy - int(150 * scale)), (cx, cy - 30)], fill=cord, width=3)
    # pendant: small glowing realm sigil
    pd = sigil(chain_name, size, tuple(min(255, int(v * 1.3)) for v in color))
    for blur, alpha in ((10, 60), (5, 95), (2, 140)):
        g = pd.filter(ImageFilter.GaussianBlur(blur)); gp = g.copy()
        put_alpha(gp, alpha)
        layer.alpha_composite(gp, (cx - size // 2, cy - size // 2))
    sharp = pd.copy(); put_alpha(sharp, 240)
    layer.alpha_composite(sharp, (cx - size // 2, cy - size // 2))
    return layer


def ascended(route):
    """THE ASCENDED 1/1: pilgrimage completion reward - a fully omni being.
    Art encodes the collector's actual route: amulet cluster + robe embroidery
    cycle the six realm sigils in the order the piece traveled them."""
    size = 1024
    gold = CHAINS["BIGNETWORK"]["primary"]
    canvas = flat_chamber(size, gold)

    body = Image.open(BASE).convert("RGBA")
    target = int(size * 0.72)
    scale = target / 897
    body = body.resize((target, target), Image.LANCZOS)

    # robe: embroidered with ALL six realm sigils, cycling in route order
    w, h = body.size
    tw = 88
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    i = 0
    row = 0
    for y in range(int(h * 0.42), h, tw):
        shift = (tw // 2) if row % 2 else 0
        for x in range(-tw, w, tw):
            chain = route[i % len(route)]
            tile = sigil(chain, 58, tuple(min(255, int(v * 1.35)) for v in CHAINS[chain]["primary"]))
            put_alpha(tile, 80)
            layer.alpha_composite(tile, (x + shift, y))
            i += 1
        row += 1
    import numpy as np
    la = np.array(layer); la[:, :, 3] = np.minimum(la[:, :, 3], np.array(body)[:, :, 3])
    body = Image.alpha_composite(body, Image.fromarray(la, "RGBA"))

    off = ((size - target) // 2, int((size - target) * 0.56))
    canvas.alpha_composite(body, off)
    canvas.alpha_composite(rim_light(body, gold), off)
    canvas = Image.alpha_composite(canvas, eye_glow(897, scale, off, (210, 190, 120), (255, 245, 205)))

    # amulet cluster: six realm pendants on a fan cord, route order
    d = ImageDraw.Draw(canvas)
    cx0 = off[0] + int(440 * scale)
    cy0 = off[1] + int(470 * scale)
    d.line([(cx0 - int(210 * scale), cy0 - int(130 * scale)), (cx0, cy0 - 20)], fill=(150, 128, 74, 255), width=3)
    d.line([(cx0 + int(210 * scale), cy0 - int(130 * scale)), (cx0, cy0 - 20)], fill=(150, 128, 74, 255), width=3)
    cluster = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cluster)
    n = len(route)
    for j, chain in enumerate(route):
        px = cx0 + (j - (n - 1) / 2) * 74
        py = cy0 + abs(j - (n - 1) / 2) * 26
        cd.line([(cx0, cy0 - 20), (px, py - 26)], fill=(150, 128, 74, 210), width=2)
        pd = sigil(chain, 74, tuple(min(255, int(v * 1.3)) for v in CHAINS[chain]["primary"]))
        for blur, alpha in ((8, 55), (3, 100)):
            g = pd.filter(ImageFilter.GaussianBlur(blur)); gp = g.copy()
            put_alpha(gp, alpha)
            cluster.alpha_composite(gp, (int(px) - 37, int(py) - 37))
        sharp = pd.copy(); put_alpha(sharp, 240)
        cluster.alpha_composite(sharp, (int(px) - 37, int(py) - 37))
    canvas = Image.alpha_composite(canvas, cluster)

    # relic staff with The Center crystal
    canvas = Image.alpha_composite(canvas, relic_staff(size, off, target, "BIGNETWORK", gold, (242, 234, 214)))

    out = canvas.convert("RGB")
    out = ground_shadow(out, int(off[1] + target * 0.965), int(target * 0.30))
    d2 = ImageDraw.Draw(out)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 30)
    except Exception:
        f = ImageFont.load_default()
    lbl = "THE ASCENDED"
    d2.text((size / 2 - d2.textlength(lbl, font=f) / 2, size - 74), lbl, font=f, fill=gold)
    return out


def vestment(body_img, color, strength=0.22):
    """rare vestment trait: lower body tinted toward the realm hue (wardens style)"""
    import numpy as np
    a = np.array(body_img).astype(float)
    h = a.shape[0]
    mask = np.linspace(0, 1, h)[:, None, None] ** 2.2   # 0 at top -> 1 at bottom
    m = (mask * strength)[..., 0][..., None]
    c = np.array(color, dtype=float)
    a[:, :, :3] = a[:, :, :3] * (1 - m) + c * m
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def relic_staff(size, off, target, chain_name, color, accent):
    """the warden's relic: staff with a glowing realm crystal (mini sigil) at the top"""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    feet_y = int(off[1] + target * 0.94)
    top_y = int(off[1] + target * 0.18)
    sx = off[0] + int(target * 0.13)
    # shaft: dark outer, light core
    d.line([(sx, feet_y), (sx, top_y)], fill=(28, 30, 40, 255), width=13)
    d.line([(sx, feet_y), (sx, top_y)], fill=(120, 122, 138, 255), width=6)
    d.line([(sx, feet_y), (sx, top_y)], fill=(190, 192, 205, 255), width=2)
    # crystal = realm sigil, glowing
    cr = sigil(chain_name, 190, tuple(min(255, int(v * 1.3)) for v in color))
    cxx, cyy = sx, top_y - 80
    for blur, alpha in ((16, 60), (9, 95), (4, 140)):
        g = cr.filter(ImageFilter.GaussianBlur(blur))
        gp = g.copy(); put_alpha(gp, alpha)
        layer.alpha_composite(gp, (cxx - 95, cyy - 95))
    sharp = cr.copy(); put_alpha(sharp, 235)
    layer.alpha_composite(sharp, (cxx - 95, cyy - 95))
    # small accent spark
    d.ellipse([cxx - 5, cyy - 5, cxx + 5, cyy + 5], fill=accent + (255,))
    return layer, cyy


def render(chain_name, spec, traits=None):
    traits = traits or {}
    TR = {
        "staff": traits.get("staff", True),
        "robe_pattern": traits.get("robe_pattern", True),
        "vestment": traits.get("vestment", False),
        "chest_sigil": traits.get("chest_sigil", True),
        "eye_mode": traits.get("eye_mode", "chain"),
        "rim": traits.get("rim", "chain"),
    }
    size = 1024
    color = spec["primary"]
    accent = spec["accent"]

    canvas = flat_chamber(size, color)

    # body: scale base to ~72% of canvas
    body = Image.open(BASE).convert("RGBA")
    target = int(size * 0.72)
    scale = target / 897
    body = body.resize((target, target), Image.LANCZOS)
    if TR["vestment"]:
        body = vestment(body, color)
    # embroidered realm motif on the robe (identity in the fabric)
    if TR["robe_pattern"]:
        body = robe_pattern(body, chain_name, color)
    # base cutout canvas is 897 with figure roughly filling it; center it slightly low
    off = ((size - target) // 2, int((size - target) * 0.56))
    canvas.alpha_composite(body, off)
    rl = rim_light(body, color if TR["rim"] == "chain" else (217, 180, 91) if TR["rim"] == "gold" else (60, 62, 74))
    canvas.alpha_composite(rl, off)

    # eye glow
    if TR["eye_mode"] == "white":
        canvas = Image.alpha_composite(canvas, eye_glow(897, scale, off, (210, 214, 224), (252, 252, 252)))
    else:
        canvas = Image.alpha_composite(canvas, eye_glow(897, scale, off, color, accent))

    # realm mark worn as an amulet accessory (per BudE: symbols as accessories)
    if TR["chest_sigil"]:
        canvas = Image.alpha_composite(canvas, amulet(chain_name, color, accent, off, scale))

    # relic staff with realm crystal (wardens concept)
    if TR["staff"]:
        canvas = Image.alpha_composite(canvas, relic_staff(size, off, target, chain_name, color, accent)[0])

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
    import json
    os.makedirs(OUT, exist_ok=True)

    # ---- canonical trait catalog ----
    traits_catalog = {
        "collection": "Lil Omnis",
        "total": 666,
        "note": "666 = six chapters x 111: ETH, Base, Robinhood, BNB, Solana, Sui.",
        "chapters": [
            {"num": "I",   "realm": "ETHEREUM",  "chamber": "The Ether Vault",   "chain_count": 111},
            {"num": "II",  "realm": "BASE",      "chamber": "The Blue Keep",     "chain_count": 111},
            {"num": "III", "realm": "ROBINHOOD", "chamber": "The Green Wood",    "chain_count": 111},
            {"num": "IV",  "realm": "BNB",       "chamber": "The Amber Temple",  "chain_count": 111},
            {"num": "V",   "realm": "SOLANA",    "chamber": "The Violet Hive",   "chain_count": 111},
            {"num": "VI",  "realm": "SUI",       "chamber": "The Tide Gate",     "chain_count": 111},
        ],
        "layers": [
            {"order": 1, "trait": "Chamber",     "type": "background",  "note": "plain near-black, faint realm floor glow - no symbols (v0.4 law: identity not from bg)"},
            {"order": 2, "trait": "Body",         "type": "base",        "note": "the shadow being - pure, unmarked, anonymous (The Unnamed doctrine)"},
            {"order": 3, "trait": "Robe Pattern", "type": "fabric",      "note": "embroidered realm sigil motif woven in a diamond grid over the robe"},
            {"order": 4, "trait": "Vestment",      "type": "body_tint",   "rare": True, "note": "lower-body robe tint toward realm hue"},
            {"order": 5, "trait": "Rim Light",     "type": "edge_glow",   "variants": ["realm color", "gilded gold (rare)"]},
            {"order": 6, "trait": "Eye Glow",      "type": "eyes",        "variants": ["realm color", "pale white (rare)"]},
            {"order": 7, "trait": "Amulet",        "type": "accessory",    "note": "realm mark worn on a cord - present/absent (absent = The Unnamed)"},
            {"order": 8, "trait": "Relic Staff",   "type": "prop",        "rare": True, "note": "warden's staff with glowing realm crystal"},
        ],
        "per_realm_allocation": {
            "total": 111,
            "standard": 60,
            "relic_staff": 25,
            "vested": 12,
            "pale_glow_eyes": 8,
            "gilded_rim": 5,
            "the_unnamed": 1,
            "note": "the 1 Unnamed per realm: no amulet, no robe pattern, pale eyes - the realm's rarest soul"
        },
        "one_of_ones": [
            {"piece": "001", "name": "THE ORIGIN", "note": "BudE's original shadow being, untouched - the genesis piece"},
        ],
        "lore": {
            "identity": "THE SHADOW BEING HAS NO NAME. Origin sealed forever (Codex Fragment 002).",
            "relics": "Each warden's crystal is the relic that opens its realm's chapter.",
        },
    }
    with open(os.path.join(HERE, "traits.json"), "w") as f:
        json.dump(traits_catalog, f, indent=2)
    print("traits.json written")

    # ---- render the six realm wardens (standard + relic staff) ----
    panels = []
    for name, spec in CHAINS.items():
        img = render(name, spec)
        img.save(os.path.join(OUT, f"omnis_{name.lower()}.png"))
        panels.append((name, img, "standard"))
        print("rendered", name)

    # ---- rarity showcase ----
    rarity = []
    # THE UNNAMED (no sigil, pale eyes, no staff) - Solana body
    rarity.append(("THE UNNAMED", render("SOLANA", CHAINS["SOLANA"],
        {"staff": False, "chest_sigil": False, "robe_pattern": False, "eye_mode": "white"})))
    # THE VESTED (robe tint + staff) - BNB
    rarity.append(("THE VESTED", render("BNB", CHAINS["BNB"],
        {"vestment": True, "staff": True})))
    # GILDED (gold rim + staff) - Base
    rarity.append(("GILDED", render("BASE", CHAINS["BASE"],
        {"rim": "gold", "staff": True})))
    # PALE GLOW (white eyes + staff) - Sui
    rarity.append(("PALE GLOW", render("SUI", CHAINS["SUI"],
        {"eye_mode": "white", "staff": True})))

    # ---- THE ORIGIN 1/1: BudE's original shadow being, untouched ----
    origin = Image.open(os.path.join(HERE, "..", "omnis-hub", "..", "lil-omnis-pipeline", "layers", "base", "base_body.png")).convert("RGBA") if False else Image.open(BASE).convert("RGBA")
    # full-body original on dark chamber, nothing added
    ocan = radial_bg(1024, (217, 180, 91)).convert("RGBA")
    tgt = int(1024 * 0.72); sc = tgt / 897
    ob = origin.resize((tgt, tgt), Image.LANCZOS)
    ocan.alpha_composite(ob, ((1024 - tgt) // 2, int((1024 - tgt) * 0.56)))
    origin_panel = ocan.convert("RGB")

    # ---- collection look sheet: 5 cols x 2 rows ----
    cell = 420
    strip = Image.new("RGB", (cell * 5, cell * 2), (3, 4, 9))
    d = ImageDraw.Draw(strip)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 17)
    except Exception:
        f_t = ImageFont.load_default()

    def put(img, idx, label, sub):
        r, c = divmod(idx, 5)
        x, y = c * cell, r * cell
        panel = img.resize((cell - 8, cell - 8), Image.LANCZOS)
        strip.paste(panel, (x + 4, y + 4))
        lw = d.textlength(label, font=f_t)
        d.text((x + (cell - lw) / 2, y + cell - 34), label, font=f_t, fill=(242, 234, 214))
        sw = d.textlength(sub, font=f_t)
        d.text((x + (cell - sw) / 2, y + cell - 14), sub, font=f_t, fill=(107, 114, 144))

    realm_names = ["ETHEREUM", "BASE", "ROBINHOOD", "BNB", "SOLANA", "SUI"]
    for i, (name, img, _) in enumerate(panels[:6]):
        put(img, i, name, "REALM WARDEN · STANDARD")
    for j, (label, img) in enumerate(rarity):
        put(img, 6 + j, label, "RARE VARIANT")
    put(origin_panel, 9, "THE ORIGIN 1/1", "PIECE #001 · GENESIS")

    strip.save(os.path.join(OUT, "collection_look.png"))

    # THE ASCENDED demo (pilgrimage completion reward)
    asc = ascended(["ETHEREUM", "BASE", "ROBINHOOD", "BNB", "SOLANA", "SUI"])
    asc.save(os.path.join(OUT, "ascended_demo.png"))
    print("saved ascended_demo.png")
    print("saved collection_look.png", strip.size)


if __name__ == "__main__":
    main()
