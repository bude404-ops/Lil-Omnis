"""LIL OMNIS collection builder: generates all 666 pieces + metadata + manifest.
Deterministic: every piece derives from seed f"{realm}-{r_index}", so the entire
collection can be regenerated bit-for-bit from this file + generate.py."""
import json, os, random, hashlib
from multiprocessing import Pool
import generate as g

OUT = "out/collection"
CHAPTERS = ["ETHEREUM", "BASE", "ROBINHOOD", "BNB", "SOLANA", "SUI"]
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}
ALLOCATION = ["standard"] * 60 + ["staff"] * 25 + ["vested"] * 12 + ["pale"] * 8 + ["gilded"] * 5

FIRST = ["Keeper", "Warden", "Seeker", "Echo", "Shade", "Herald", "Steward", "Vigil", "Watcher", "Cipher"]
SECOND = ["of the Silent Gate", "of Ember Dust", "of the Veiled Deep", "of Hollow Stars",
          "of the First Echo", "of Gilded Dust", "of the Pale Vigil", "of the Ninth Seal",
          "of Moss and Cipher", "of the Long Dark", "of Sealed Doors", "of the Quiet Flame"]

CLASS_TRAITS = {
    "standard": {"staff": False},
    "staff":    {"staff": True},
    "vested":   {"staff": False, "vestment": True},
    "pale":     {"staff": False, "eye_mode": "white"},
    "gilded":   {"staff": False, "rim": "gold"},
}


def piece(realm, ri):
    """returns (token, filename, traits_dict, epithet, class_name)"""
    ch = CHAPTERS.index(realm) + 1
    token = (ch - 1) * 111 + ri
    if ri == 111:
        traits = {"staff": False, "chest_sigil": False, "robe_pattern": False,
                  "eye_mode": "white", "rim": "dim", "seed": f"{realm}-{ri}"}
        cls = "THE UNNAMED"
        epithet = "The Unnamed"
    else:
        order = random.Random(f"alloc-{realm}").sample(ALLOCATION, len(ALLOCATION))
        kind = order[ri - 1]
        traits = dict(CLASS_TRAITS[kind])
        traits["seed"] = f"{realm}-{ri}"
        cls = {"standard": "Standard", "staff": "Relic Staff", "vested": "Vested",
               "pale": "Pale Glow", "gilded": "Gilded"}[kind]
        er = random.Random(f"name-{realm}-{ri}")
        epithet = f"The {er.choice(FIRST)} {er.choice(SECOND)}" if er.random() < 0.55 else ""
    fname = f"{token:03d}_{realm.lower()}.png"
    return token, fname, traits, epithet, cls


def render_one(args):
    realm, ri = args
    token, fname, traits, epithet, cls = piece(realm, ri)
    img = g.render(realm, g.CHAINS[realm], traits)
    path = os.path.join(OUT, fname)
    img.save(path, optimize=True)
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    meta = {
        "token": token,
        "name": f"Lil Omnis #{token:03d}",
        "epithet": epithet,
        "realm": realm,
        "chapter": ROMAN[CHAPTERS.index(realm) + 1],
        "class": cls,
        "file": fname,
        "sha256": sha,
        "attributes": [
            {"trait_type": "Realm", "value": realm},
            {"trait_type": "Chapter", "value": ROMAN[CHAPTERS.index(realm) + 1]},
            {"trait_type": "Class", "value": cls},
            {"trait_type": "Epithet", "value": epithet or "None"},
            {"trait_type": "Glyph Carriers", "value": "Robe Embroidery + Amulet" if cls != "THE UNNAMED" else "None"},
            {"trait_type": "Eyes", "value": "Pale" if traits.get("eye_mode") == "white" else "Realm Glow"},
            {"trait_type": "Rim Light", "value": "Gilded" if traits.get("rim") == "gold" else "Dim" if traits.get("rim") == "dim" else "Realm"},
            {"trait_type": "Relic Staff", "value": "Yes" if traits.get("staff") else "No"},
            {"trait_type": "Vestment", "value": "Yes" if traits.get("vestment") else "No"},
        ],
    }
    return meta


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = [(realm, ri) for realm in CHAPTERS for ri in range(1, 112)]
    with Pool(8) as pool:
        metas = pool.map(render_one, jobs)
    metas.sort(key=lambda m: m["token"])

    with open(os.path.join(OUT, "metadata.jsonl"), "w") as f:
        for m in metas:
            f.write(json.dumps(m) + "\n")

    # integrity: 666 unique hashes
    hashes = [m["sha256"] for m in metas]
    assert len(metas) == 666 and len(set(hashes)) == 666, "DUPLICATE PIECES"

    from collections import Counter
    counts = Counter((m["realm"], m["class"]) for m in metas)
    manifest = {
        "collection": "LIL OMNIS",
        "generated": "2026-10-22",
        "generator": "generate.py v0.5 (seeded, deterministic)",
        "total": 666,
        "image_size": 1024,
        "distinct_hashes": len(set(hashes)),
        "realms": {r: {c: counts[(r, c)] for c in ["Standard", "Relic Staff", "Vested", "Pale Glow", "Gilded", "THE UNNAMED"]} for r in CHAPTERS},
        "genesis": {"piece": "000_the_origin.png", "note": "BudE's original shadow being, untouched - minted before the 666"},
    }
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    print("DONE: 666 pieces,", len(set(hashes)), "distinct")


if __name__ == "__main__":
    main()
