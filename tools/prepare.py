#!/usr/bin/env python3
"""Parse the 100-character source pack into structured JSON + optimized WebP assets."""
import json, os, re, sys, unicodedata
from PIL import Image

WS = "/Users/apple/.openclaw-autoclaw/workspace"
ATT = f"{WS}/.openclaw-attachments"
NAMES_MD = f"{ATT}/20260916-133715-facde735-51b-Full List of 100 Animals and Character Names.md"
PROMPTS_MD = f"{ATT}/20260916-133715-da67d807-0b6-100 Cute Animal Reference Character Prompts full list.md"
MASTER_MD = f"{ATT}/20260916-133715-1433e5a9-e29-Master Prompt for Cute Animal Character Reference Sheets.md"
IMGDIR = f"{ATT}/20260916-133715-be06cc42-029-all animal"

PROJ = f"{WS}/projects/website-3be034e7d23b7541b70da4fb"
TMP = f"{WS}/.openclaw/tmp/build"

CATEGORIES = {
    "pets-farm": ("Pets & Farm", "Domestic companions and farmyard friends.", "15"),
}


def slugify(name, species):
    s = f"{name} {species}".lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def parse_names():
    """-> list of (idx, species, name) ordered by number."""
    out = {}
    for line in open(NAMES_MD, encoding="utf-8"):
        m = re.match(r"\s*(\d+)\.\s*(.+?)\s*—\s*\*\*(.+?)\*\*\s*$", line.strip())
        if m:
            out[int(m.group(1))] = (m.group(2).strip(), m.group(3).strip())
    return out


def parse_prompts():
    """-> dict idx -> {'name','species','paras'}. Split on headings, not on '---',
    because the source pack has at least one missing separator."""
    raw = open(PROMPTS_MD, encoding="utf-8").read()
    lines = raw.split("\n")
    heads = []
    for i, ln in enumerate(lines):
        m = re.match(r"^#\s*(\d+)\.\s*(.+?)\s*—\s*(.+?)\s*$", ln.strip())
        if m:
            heads.append((i, int(m.group(1)), m.group(2).strip(), m.group(3).strip()))
    out = {}
    for k, (i, idx, name, species) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        body = "\n".join(lines[i + 1:end])
        body = re.sub(r"\n-{3,}\s*$", "", body.strip())
        body = re.sub(r"^\*\*Character Reference Sheet Prompt\*\*\s*", "", body.strip())
        paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        out[idx] = {"name": name, "species": species, "paras": paras}
    return out


NUMWORD = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten"}


def uniq_n(items):
    seen, out = {}, []
    for it in items:
        k = it.lower()
        if k in seen:
            continue
        seen[k] = 1
        out.append(it)
    return out


def extract(paras):
    """Pull enrichment fields out of the paragraph-form prompt ('' -> segment split)."""
    text = "\n".join(paras)
    flat = re.sub(r"\s+", " ", text)
    segs = []
    for p in paras:
        for s in p.split("→"):
            s = re.sub(r"\s+", " ", s).strip()
            if s:
                segs.append(s)
    d = {}

    def q(pattern, src=None, flags=re.I):
        m = re.search(pattern, src if src is not None else flat, flags)
        return m.group(1).strip() if m else None

    def seg_after(needle):
        for s in segs:
            i = s.lower().find(needle)
            if i >= 0:
                return s[i + len(needle):].strip()
        return None

    tag = q(r'tagline\s*[“"]([^”"]+)[”"]')
    if tag:
        parts = [x.strip(" .,") for x in re.split(r"/", tag) if x.strip(" .,")]
        if parts:
            d["tagline"] = parts

    tr = q(r'traits[^“”"]{0,90}[“"]([^”"]+)[”"]')
    if tr:
        d["traits"] = uniq_n([x.strip(" .,") for x in tr.split("/") if x.strip(" .,")])

    pal = seg_after("swatches")
    if pal:
        pal = re.sub(r"^(with\s+clean\s+uppercase\s+labels\s*:?|labeled\s*:?|:\s*)\s*", "", pal, flags=re.I)
        d["palette"] = uniq_n(
            [x.strip(" .,") for x in re.split(r",|\band\b", pal) if x.strip(" .,")]
        )[:6]

    h = q(r'APPROX\.?\s*([0-9]+(?:\.[0-9]+)?\s*(?:CM|MM|M)[^”"]*)')
    if h:
        d["height"] = h.strip(" .,")

    bio = None
    for s in segs:
        m = re.search(r'\bbio\s+(?:describing\s+([A-Z][A-Za-z\-]+)\s+as|about)\s+(.+)$', s, re.I)
        if m:
            bio = (f"{m.group(1)} — {m.group(2)}" if m.group(1) else m.group(2)).strip()
            break
    if bio:
        d["bio"] = bio.strip(" .,")

    ex = seg_after("row of 4")
    if ex and ":" in ex:
        d["expressions"] = uniq_n(
            [x.strip(" .,") for x in ex.split(":", 1)[1].split(",") if x.strip(" .,")]
        )[:4]

    mac = None
    for s in segs:
        m = re.search(r'macro[^:]{0,40}panels?\s+labeled\s+(.+)$', s, re.I)
        if m:
            mac = re.split(r",\s*showing\b", m.group(1))[0]
            break
    if mac:
        d["macros"] = uniq_n(
            [x.strip(" .,") for x in re.split(r",|\band\b", mac) if x.strip(" .,")]
        )[:4]

    rend = None
    for s in segs:
        if re.match(r"^8k render", s, re.I):
            rend = s
            break
    if rend:
        d["rendering"] = rend

    return d


def find_image(idx, name, species, files):
    nb = re.compile(r"\b" + re.escape(name.lower()) + r"\b")
    toks = [t for t in re.findall(r"[a-z]+", species.lower()) if len(t) >= 3]
    hits = []
    for f in files:
        fl = f.lower().replace("—", " ").replace("-", " ")
        if not nb.search(fl):
            continue
        score = sum(1 for t in toks if t in fl)
        if score:
            hits.append((score, f))
    if not hits:
        return None
    hits.sort(key=lambda x: (-x[0], len(x[1])))
    return hits[0][1]


def main():
    names = parse_names()
    prompts = parse_prompts()
    files = sorted(os.listdir(IMGDIR))
    files = [f for f in files if f.lower().endswith(".webp")]

    missing = []
    chars = []
    used = set()
    for i in range(1, 101):
        species, name = names[i]
        p = prompts.get(i, {})
        img = find_image(i, name, species, files)
        if not img:
            missing.append((i, name, species))
            continue
        used.add(img)
        slug = slugify(name, species)
        c = {
            "n": i,
            "name": name,
            "species": species,
            "slug": slug,
            "img": img,
            "prompt": p.get("paras", []),
        }
        c.update(extract(p.get("paras", [])))
        chars.append(c)

    print(f"characters: {len(chars)}  missing images: {missing}")
    print(f"unused image files: {sorted(set(files) - used)}")
    dupes = {}
    for c in chars:
        dupes.setdefault(c["slug"], []).append(c["n"])
    bad = {k: v for k, v in dupes.items() if len(v) > 1}
    print(f"slug collisions: {bad}")

    os.makedirs(TMP, exist_ok=True)
    with open(f"{TMP}/characters.json", "w", encoding="utf-8") as fh:
        json.dump(chars, fh, ensure_ascii=False, indent=1)
    print("wrote characters.json")
    for c in chars[:2]:
        print(json.dumps(c, ensure_ascii=False)[:600])


if __name__ == "__main__":
    main()
