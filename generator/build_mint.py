#!/usr/bin/env python3
"""Lil Omnis mint builder — deterministic 666-piece assembly + export.

Pipeline stages:
  --dry-run   assign traits to all 666 tokens (seeded, reproducible), write
              mint/assignment.json + mint/trait_counts.json. No rendering.
  --sample    render ONE standard piece per realm as a smoke test.
  --full      render all 666 images + ERC-721 metadata into mint/chains/<realm>/
              (resumable — skips tokens whose image already exists).

Everything is driven by generator/traits.json (chapters + per-realm allocation)
and a fixed seed so the collection is reproducible forever.

Usage:
  python3 build_mint.py --dry-run
  python3 build_mint.py --sample
  python3 build_mint.py --full [--image-base ipfs://__CID__/]
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GEN = os.path.join(REPO, "generator")
MINT = os.path.join(REPO, "mint")

SEED = "lil-omnis-666-v1"
TOTAL = 666
PER_REALM = 111

# Allocation class -> render trait spec.
# NOTE: relic_staff visual differentiation lands with the art-upgrade pass
# (reference-derived layers per the art quality law); the class is recorded
# in metadata now so rarity is correct regardless of art timing.
CLASS_TRAITS = {
    "standard":        {"staff": True, "robe_pattern": True, "chest_sigil": True, "eye_mode": "chain", "rim": "chain"},
    "relic_staff":     {"staff": True, "robe_pattern": True, "chest_sigil": True, "eye_mode": "chain", "rim": "chain"},
    "vested":          {"staff": True, "robe_pattern": True, "chest_sigil": True, "vestment": True, "eye_mode": "chain", "rim": "chain"},
    "pale_glow_eyes":  {"staff": True, "robe_pattern": True, "chest_sigil": True, "eye_mode": "white", "rim": "chain"},
    "gilded_rim":      {"staff": True, "robe_pattern": True, "chest_sigil": True, "eye_mode": "chain", "rim": "gold"},
    "the_unnamed":     {"staff": False, "robe_pattern": False, "chest_sigil": False, "eye_mode": "white", "rim": "plain"},
}

CLASS_LABEL = {
    "standard": "Standard Warden",
    "relic_staff": "Relic Staff Bearer",
    "vested": "Vested Warden",
    "pale_glow_eyes": "Pale-Eyed Warden",
    "gilded_rim": "Gilded Rim Warden",
    "the_unnamed": "The Unnamed",
}

DESCRIPTION = (
    "Lil Omnis — 666 shadow beings across six realms. Six chapters of 111, "
    "one per chain: Ethereum, Base, Robinhood, BNB, Solana, Sui. The shadow being has no name."
)


def load_traits():
    with open(os.path.join(GEN, "traits.json")) as f:
        return json.load(f)


def build_assignment():
    """Deterministic global assignment. Returns list of 666 token records."""
    traits = load_traits()
    alloc = traits["per_realm_allocation"]
    classes = [k for k in CLASS_TRAITS if k in alloc and k != "total"]
    rng = random.Random(SEED)
    records = []
    edition = 1
    for ch in traits["chapters"]:
        realm = ch["realm"].lower()
        pool = []
        for cls in classes:
            pool += [cls] * int(alloc[cls])
        assert len(pool) == PER_REALM, f"{realm}: allocation sums {len(pool)} != {PER_REALM}"
        rng.shuffle(pool)
        for i in range(PER_REALM):
            records.append({
                "edition": edition,                    # global 1..666
                "token_in_chain": i + 1,              # 1..111 on its chain
                "chain": ch["realm"],
                "chapter": ch["num"],
                "chamber": ch["chamber"],
                "klass": pool[i],
                "traits": dict(CLASS_TRAITS[pool[i]]),
            })
            edition += 1
    assert len(records) == TOTAL
    return records


def trait_counts(records):
    counts = {}
    for r in records:
        key = r["chain"] + "/" + r["klass"]
        counts[key] = counts.get(key, 0) + 1
    return counts


def metadata_for(rec, image_base):
    return {
        "name": f"Lil Omnis #{rec['edition']:03d} — {CLASS_LABEL[rec['klass']]}",
        "description": DESCRIPTION,
        "image": f"{image_base}images/{rec['token_in_chain']:03d}.png",
        "edition": rec["edition"],
        "chapter": rec["chapter"],
        "chain": rec["chain"],
        "attributes": [
            {"trait_type": "Chapter", "value": rec["chapter"]},
            {"trait_type": "Realm", "value": rec["chain"]},
            {"trait_type": "Chamber", "value": rec["chamber"]},
            {"trait_type": "Class", "value": CLASS_LABEL[rec["klass"]]},
        ],
    }


def dry_run():
    records = build_assignment()
    os.makedirs(MINT, exist_ok=True)
    with open(os.path.join(MINT, "assignment.json"), "w") as f:
        json.dump({"seed": SEED, "total": TOTAL, "tokens": records}, f, indent=1)
    counts = trait_counts(records)
    with open(os.path.join(MINT, "trait_counts.json"), "w") as f:
        json.dump(counts, f, indent=1)
    print(f"assignment written: {TOTAL} tokens, seed {SEED}")
    for k in sorted(counts):
        print(f"  {k:28s} {counts[k]}")


def _render_chain():
    sys.path.insert(0, GEN)
    import generate  # noqa
    return generate


def render_records(records, image_base):
    gen = _render_chain()
    os.makedirs(MINT, exist_ok=True)
    for rec in records:
        rdir = os.path.join(MINT, "chains", rec["chain"].lower())
        idir = os.path.join(rdir, "images")
        mdir = os.path.join(rdir, "metadata")
        os.makedirs(idir, exist_ok=True)
        os.makedirs(mdir, exist_ok=True)
        ipath = os.path.join(idir, f"{rec['token_in_chain']:03d}.png")
        if not os.path.exists(ipath):
            spec = gen.CHAINS[rec["chain"]]
            img = gen.render(rec["chain"], spec, rec["traits"])
            img.save(ipath)
        with open(os.path.join(mdir, f"{rec['token_in_chain']:03d}.json"), "w") as f:
            json.dump(metadata_for(rec, image_base), f, indent=1)
        print(f"edition {rec['edition']:03d} -> {rec['chain']}/{rec['token_in_chain']:03d}")


def sample():
    records = build_assignment()
    picks = []
    for ch in load_traits()["chapters"]:
        realm = ch["realm"]
        picks.append(next(r for r in records if r["chain"] == realm and r["klass"] == "standard"))
    render_records(picks, "")
    print("sample rendered:", ", ".join(p["chain"] for p in picks))


def full(image_base):
    records = build_assignment()
    render_records(records, image_base)
    # provenance manifest
    manifest = {"seed": SEED, "total": TOTAL, "files": {}}
    for root, _, files in os.walk(MINT):
        for fn in files:
            if fn.endswith(".png"):
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, MINT)
                manifest["files"][rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    with open(os.path.join(MINT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"full render done: {len(manifest['files'])} images, manifest written")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--image-base", default="ipfs://REPLACE_CID__/", help="base URI for image links in metadata")
    args = ap.parse_args()
    if args.dry_run:
        dry_run()
    elif args.sample:
        sample()
    elif args.full:
        full(args.image_base)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
