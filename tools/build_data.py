#!/usr/bin/env python3
"""Assign categories, build prompt text, emit character data + optimized WebP assets."""
import json, os, re
from PIL import Image

WS = "/Users/apple/.openclaw-autoclaw/workspace"
ATT = f"{WS}/.openclaw-attachments"
IMGDIR = f"{ATT}/20260916-133715-be06cc42-029-all animal"
PROJ = f"{WS}/projects/website-3be034e7d23b7541b70da4fb"
TMP = f"{WS}/.openclaw/tmp/build"

CATS = [
    ("pets-farm", "Pets & Farm", "Domestic companions and farmyard friends."),
    ("forest-meadow", "Forest & Meadow", "Small wild mammals of woods, fields and gardens."),
    ("jungle-savanna", "Jungle & Savanna", "Primates and big-animal adventurers."),
    ("ocean-reef", "Ocean & Reef", "Marine mammals, fish and reef dwellers."),
    ("birds-sky", "Birds & Sky", "Feathered friends from flamingo to puffin."),
    ("reptiles-amphibians", "Reptiles & Amphibians", "Scaly, slithery and slippery characters."),
    ("tiny-critters", "Tiny Critters", "Insects and the very small."),
]

ASSIGN = {
    "pets-farm": [1, 2, 3, 4, 21, 22, 23, 24, 25, 26, 27, 28, 32, 82, 97],
    "forest-meadow": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                      29, 30, 31, 91, 96, 98, 99],
    "jungle-savanna": [33, 34, 35, 36, 37, 38, 39, 40, 41, 94, 100],
    "ocean-reef": [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                   57, 58, 59, 60, 61, 92],
    "birds-sky": [71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 83, 84, 85, 86, 87, 93],
    "reptiles-amphibians": [62, 63, 64, 65, 66, 67, 68, 69, 70, 95],
    "tiny-critters": [88, 89, 90],
}


def clean_prompt(paras):
    out = []
    for p in paras:
        t = re.sub(r"\s*→\s*$", "", p.strip())
        t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
        t = re.sub(r"[ \t]+", " ", t).strip()
        # preserve the "row of 4 expressions: a, b, c, d" -> keep inline
        if t:
            out.append(t)
    return "\n\n".join(out)


def main():
    chars = json.load(open(f"{TMP}/characters.json", encoding="utf-8"))
    idx2cat = {i: cid for cid, lst in ASSIGN.items() for i in lst}
    catmeta = {cid: (label, desc) for cid, label, desc in CATS}

    # sanity
    assert sorted(idx2cat) == list(range(1, 101)), sorted(set(range(1, 101)) - set(idx2cat))

    for c in chars:
        c["cat"] = idx2cat[c["n"]]
        c["catLabel"] = catmeta[c["cat"]][0]
        c["promptText"] = clean_prompt(c["prompt"])
        del c["prompt"]

    chars.sort(key=lambda c: c["n"])
    for i, c in enumerate(chars):
        c["prevN"] = chars[(i - 1) % len(chars)]["n"]
        c["nextN"] = chars[(i + 1) % len(chars)]["n"]

    counts = {}
    for c in chars:
        counts[c["cat"]] = counts.get(c["cat"], 0) + 1

    # ── assets ────────────────────────────────────────────────────────────
    thumbs = f"{PROJ}/assets/thumbs"
    full = f"{PROJ}/assets/full"
    data = f"{PROJ}/assets/data"
    for d in (thumbs, full, data):
        os.makedirs(d, exist_ok=True)

    tsizes = fsizes = 0
    for c in chars:
        src = f"{IMGDIR}/{c['img']}"
        im = Image.open(src).convert("RGB")
        w, h = im.size

        tw = 560
        t = im.resize((tw, round(h * tw / w)), Image.LANCZOS)
        tp = f"{thumbs}/{c['slug']}.webp"
        t.save(tp, "WEBP", quality=70, method=5)
        tsizes += os.path.getsize(tp)

        fw = 1120
        f = im.resize((fw, round(h * fw / w)), Image.LANCZOS)
        fp = f"{full}/{c['slug']}.webp"
        f.save(fp, "WEBP", quality=72, method=5)
        fsizes += os.path.getsize(fp)

        c["thumb"] = f"assets/thumbs/{c['slug']}.webp"
        c["full"] = f"assets/full/{c['slug']}.webp"

    print(f"thumbs total {tsizes/1e6:.2f} MB | full total {fsizes/1e6:.2f} MB | "
          f"combined {(tsizes+fsizes)/1e6:.2f} MB")
    print("counts:", counts)

    light = [{k: c[k] for k in ("n", "name", "species", "slug", "cat", "catLabel",
                                "tagline", "traits", "palette", "height", "bio",
                                "thumb", "full", "prevN", "nextN")} for c in chars]
    with open(f"{data}/characters.js", "w", encoding="utf-8") as fh:
        fh.write("window.CATEGORIES=" + json.dumps(
            [{"id": cid, "label": lb, "desc": d, "count": counts.get(cid, 0)}
             for cid, lb, d in CATS], ensure_ascii=False) + ";\n")
        fh.write("window.CHARACTERS=" + json.dumps(light, ensure_ascii=False) + ";\n")

    with open(f"{TMP}/full.json", "w", encoding="utf-8") as fh:
        json.dump(chars, fh, ensure_ascii=False, indent=1)
    print("wrote characters.js + full.json")


if __name__ == "__main__":
    main()
