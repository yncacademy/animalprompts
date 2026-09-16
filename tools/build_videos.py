#!/usr/bin/env python3
"""Map the 100 showcase videos to characters, transcode for web, extract posters.

Mapping rules (verified against the pack):
  * 'Echo Bat Character Showcase.mp4'      -> name token + species hint
  * 'Marina Manatee ...' vs 'Marina ...'   -> hinted file wins the hinted species
  * user decisions: 'Clover ... 1.mp4' -> Domestic Lamb, 'Sunny ... 1.mp4' -> Quokka
Outputs: <repo>/assets/videos/<slug>.mp4 + posters/<slug>.webp + manifest.json
"""
import base64, json, os, re, subprocess, sys, unicodedata

WS = "/Users/apple/.openclaw-autoclaw/workspace"
VD = f"{WS}/animal video file"
FULL = f"{WS}/.openclaw/tmp/build/full.json"
REPO = f"{WS}/github-repo/animalprompts"
OUT = f"{REPO}/assets/videos"
POSTERS = f"{OUT}/posters"
FF = subprocess.run(
    [sys.executable, "-c", "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"],
    capture_output=True, text=True).stdout.strip()

# user disambiguation (form answers)
USER_DECIDE = {
    ("clover", "1"): "clover-domestic-lamb",        # Clover Character Showcase 1.mp4
    ("clover", ""): "clover-capybara",              # Clover Character Showcase.mp4
    ("sunny", "1"): "sunny-quokka",                 # Sunny Character Showcase 1.mp4
    ("sunny", ""): "sunny-american-alligator",      # Sunny Character Showcase.mp4
}


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def name_key(fname):
    k = re.sub(r"\.mp4$", "", fname, flags=re.I)
    k = re.sub(r"charactershowcase", "", norm(k))
    k = re.sub(r"1$", "", k)
    return k


def map_videos():
    chars = json.load(open(FULL, encoding="utf-8"))
    by_slug = {c["slug"]: c for c in chars}
    files = sorted(f for f in os.listdir(VD) if f.lower().endswith(".mp4"))
    assert len(files) == 100, f"expected 100 videos, found {len(files)}"

    def species_hit(c, hint):
        return bool(hint) and hint in norm(c["species"])

    assign = {}
    used = set()
    problems = []

    # two passes: deterministic matches first, leftovers via user table / elimination
    pending = []
    for f in files:
        key = name_key(f)                      # e.g. 'marinamanatee', 'inky', 'clover'
        cands = [c for c in chars if key.startswith(norm(c["name"]))]
        if not cands:
            problems.append((f, "no name match"))
            continue
        longest = max(len(norm(c["name"])) for c in cands)
        top = [c for c in cands if len(norm(c["name"])) == longest]  # longest-name wins
        hint = key[longest:]
        pick = None
        if len(top) == 1:
            pick = top[0]
        else:
            hinted = [c for c in top if species_hit(c, hint)]
            if len(hinted) == 1:
                pick = hinted[0]
            else:
                pending.append((f, top))
                continue
        if pick["slug"] in used:
            problems.append((f, f"slug {pick['slug']} already assigned"))
            continue
        used.add(pick["slug"])
        assign[pick["slug"]] = f

    # leftovers: clover/sunny pairs + anything elimination can settle
    still = []
    for f, top in pending:
        nm = norm(re.sub(r"\s?1\.mp4$", "", f, flags=re.I).replace("Character Showcase", "").strip())
        is_one = bool(re.search(r"\s1\.mp4$", f, re.I))
        dec = USER_DECIDE.get((nm, "1" if is_one else ""))
        if dec and dec not in used:
            pick = by_slug[dec]
            used.add(pick["slug"])
            assign[pick["slug"]] = f
        else:
            still.append((f, top))

    # elimination pass: candidate already taken elsewhere -> the other one is ours
    for f, top in still:
        free = [c for c in top if c["slug"] not in used]
        if len(free) == 1:
            used.add(free[0]["slug"])
            assign[free[0]["slug"]] = f
        else:
            problems.append((f, f"unresolved, free={[c['slug'] for c in free]}"))

    missing = [c["slug"] for c in chars if c["slug"] not in assign]
    return assign, problems, missing


def probe_ok(path):
    r = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True)
    return "Duration" in r.stderr


def transcode(src, dst):
    cmd = [FF, "-hide_banner", "-loglevel", "error", "-y", "-i", src,
           "-vf", "scale=720:1280:flags=lanczos",
           "-c:v", "libx264", "-preset", "medium", "-crf", "23",
           "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", dst]
    subprocess.run(cmd, check=True)


def poster(src, dst):
    png = dst + ".tmp.png"
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", src,
                    "-frames:v", "1", png], check=True)
    from PIL import Image
    im = Image.open(png).convert("RGB")
    im.save(dst, "WEBP", quality=68, method=5)
    os.remove(png)


def main():
    os.makedirs(POSTERS, exist_ok=True)
    assign, problems, missing = map_videos()
    print(f"mapped {len(assign)}/100 | problems: {problems} | missing: {missing}")
    if problems or missing:
        sys.exit(2)

    manifest = {}
    sizes = []
    import time
    t0 = time.time()
    for i, (slug, fname) in enumerate(sorted(assign.items(), key=lambda kv: kv[0]), 1):
        src = os.path.join(VD, fname)
        mp4 = os.path.join(OUT, slug + ".mp4")
        webp = os.path.join(POSTERS, slug + ".webp")
        if not os.path.exists(mp4):
            transcode(src, mp4)
        if not os.path.exists(webp):
            poster(src, webp)
        sz = os.path.getsize(mp4)
        sizes.append(sz)
        manifest[slug] = {"mp4": f"assets/videos/{slug}.mp4",
                          "poster": f"assets/videos/posters/{slug}.webp"}
        if i % 10 == 0:
            el = time.time() - t0
            avg = sum(sizes) / len(sizes) / 1e6
            print(f"  {i}/100 done | avg {avg:.2f} MB | elapsed {el/60:.1f} min", flush=True)

    with open(f"{OUT}/manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)
    total = sum(sizes) / 1e6
    print(f"DONE {len(sizes)} videos | total {total:.1f} MB | avg {total/len(sizes):.2f} MB "
          f"| max {max(sizes)/1e6:.2f} MB | {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
