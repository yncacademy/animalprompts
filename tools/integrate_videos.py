#!/usr/bin/env python3
"""Add video integration to the GitHub repo copy: homepage featured strip,
detail-page video section, and nav link. Idempotent; source = repo copy itself."""
import json, os, re

REPO = "/Users/apple/.openclaw-autoclaw/workspace/github-repo/animalprompts"
VIDDIR = "/Users/apple/.openclaw-autoclaw/workspace/animal video file"


def esc(s):
    import html
    return html.escape(str(s if s is not None else ""), quote=True)


def load_manifest():
    p = f"{REPO}/assets/videos/manifest.json"
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return None


def pick_featured(manifest, chars, n=8):
    """Deterministic, visually strong picks spread across collections."""
    by_slug = {c["slug"]: c for c in chars}
    wanted = ["whiskers-domestic-cat", "maple-red-panda", "biscuit-golden-retriever-puppy",
              "tambo-baby-elephant", "nova-baby-penguin", "bloom-axolotl",
              "dune-fennec-fox", "koa-koala"]
    return [by_slug[s] for s in wanted if s in manifest]


# ── index.html: featured strip ──────────────────────────────────────────────
def load_chars():
    raw = open(f"{REPO}/assets/data/characters.js", encoding="utf-8").read()
    return json.loads(raw.split("window.CHARACTERS=")[1].strip().rstrip(";\n"))


def patch_index(manifest):
    p = f"{REPO}/index.html"
    s = open(p, encoding="utf-8").read()
    if "featured-videos" in s:
        print("index already patched")
        return
    chars = load_chars()
    featured = pick_featured(manifest, chars)

    def thumb(c):
        return f'''<a class="video-thumb" href="character/{c['slug']}.html" data-slug="{c['slug']}"
       data-video-src="{manifest[c['slug']]['mp4']}"
       data-video-poster="{manifest[c['slug']]['poster']}"
       data-name="{esc(c['name'])}">
        <img src="{c['thumb']}" width="560" height="700" loading="lazy" decoding="async"
             alt="{esc(c['name'])} animation thumbnail">
        <span class="play-badge" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.5v13l11-6.5z"/></svg>
        </span>
        <span class="vname">{esc(c['name'])}</span>
      </a>'''

    main_slug = featured[0]["slug"]
    strip = f'''
<section class="featured-videos" aria-labelledby="fv-h">
  <div class="container">
    <div class="featured-caption-row">
      <div>
        <span class="kicker">Character animations</span>
        <h2 id="fv-h" style="font-size:var(--fs-h2)">Watch them move</h2>
      </div>
      <span class="featured-note">5-second showcases generated from each character sheet</span>
    </div>
    <div class="featured-main" data-featured-main>
      <div class="placeholder">
        <div>
          <b>Press a character below to play</b>
          <p>Every one of the 100 characters has a short animated showcase — click any portrait to watch it here, or open a character page for its full sheet.</p>
        </div>
      </div>
    </div>
    <div class="featured-row" data-featured-videos>
      {''.join(thumb(c) for c in featured)}
    </div>
    <p class="featured-note" style="margin-top:10px">
      Now playing: <span class="featured-caption">{esc(featured[0]['name'])}</span>
      · <a href="character/{main_slug}.html">open {esc(featured[0]['name'])}&rsquo;s full sheet</a>
    </p>
  </div>
</section>
'''
    # insert before the subscribe section
    anchor = '<section class="subscribe"'
    assert anchor in s
    s = s.replace(anchor, strip + "\n" + anchor, 1)
    # script include
    s = s.replace('<script src="assets/js/app.js"></script>',
                  '<script src="assets/js/app.js"></script>\n<script src="assets/js/videos.js"></script>')
    open(p, "w", encoding="utf-8").write(s)
    print("index.html: featured strip added")


# ── detail pages: video section ─────────────────────────────────────────────
def patch_detail_pages(manifest):
    n = 0
    for slug, meta in manifest.items():
        p = f"{REPO}/character/{slug}.html"
        if not os.path.exists(p):
            print("  MISSING page:", slug)
            continue
        s = open(p, encoding="utf-8").read()
        if "video-block" in s:
            continue
        chars = load_chars()
        c = next(x for x in chars if x["slug"] == slug)

        section = f'''
    <section class="video-block" data-video-src="../{meta['mp4']}" data-video-poster="../{meta['poster']}" aria-label="Character animation video">
      <div class="video-stage">
        <img class="video-poster" src="../{meta['poster']}" width="720" height="1280" loading="lazy" decoding="async"
             alt="Poster frame of the {esc(c['name'])} animation">
        <button type="button" class="video-play" aria-label="Play the {esc(c['name'])} animation">
          <span class="play-btn" aria-hidden="true">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.5v13l11-6.5z"/></svg>
          </span>
          <span class="hint">Play the {esc(c['name'])} animation</span>
        </button>
      </div>
      <div class="video-meta">
        <span class="pill-v"><span class="dotv" aria-hidden="true"></span>Animated showcase</span>
        <span>5 seconds &middot; no sound</span>
      </div>
    </section>
'''
        anchor = '<nav class="container pager"'
        assert anchor in s, slug
        s = s.replace(anchor, section + "\n" + anchor, 1)
        s = s.replace('<script src="../assets/js/detail.js"></script>',
                      '<script src="../assets/js/detail.js"></script>\n<script src="../assets/js/videos.js"></script>')
        open(p, "w", encoding="utf-8").write(s)
        n += 1
    print(f"detail pages patched: {n}")


# ── about.html: mention the videos ──────────────────────────────────────────
def patch_about(manifest):
    p = f"{REPO}/about.html"
    s = open(p, encoding="utf-8").read()
    if "Animated showcases" in s:
        return
    old = """    <h2>How the characters were made</h2>"""
    new = """    <h2>Beyond the still sheets</h2>
    <p>All 100 characters also have a <strong>five-second animated showcase</strong> — a short
      generated clip that brings the reference sheet into motion. Each character page carries
      its clip beneath the sheet, and the homepage features a strip of them. Like the sheets,
      the animations were generated from prompts built on the same master template.</p>

    <h2>How the characters were made</h2>"""
    assert old in s
    s = s.replace(old, new, 1)
    open(p, "w", encoding="utf-8").write(s)
    print("about.html updated")


def fix_relative_paths(manifest):
    """Repair detail pages patched with root-relative video paths (they resolve
    against /character/ and 404). Idempotent fixup."""
    n = 0
    for slug in manifest:
        p = f"{REPO}/character/{slug}.html"
        if not os.path.exists(p):
            continue
        s = open(p, encoding="utf-8").read()
        if 'data-video-src="assets/videos/' not in s:
            continue
        s = s.replace('data-video-src="assets/videos/', 'data-video-src="../assets/videos/')
        s = s.replace('data-video-poster="assets/videos/', 'data-video-poster="../assets/videos/')
        s = s.replace('src="assets/videos/posters/', 'src="../assets/videos/posters/')
        open(p, "w", encoding="utf-8").write(s)
        n += 1
    print("relative-path fixups:", n)


if __name__ == "__main__":
    m = load_manifest()
    if not m:
        raise SystemExit("manifest.json not found — run build_videos.py first")
    print(f"manifest: {len(m)} videos")
    fix_relative_paths(m)
    patch_index(m)
    patch_detail_pages(m)
    patch_about(m)
