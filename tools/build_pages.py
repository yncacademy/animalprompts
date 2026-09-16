#!/usr/bin/env python3
"""Generate index.html, about.html, master-prompt.html and 100 character pages."""
import html, json, os, re

WS = "/Users/apple/.openclaw-autoclaw/workspace"
PROJ = f"{WS}/projects/website-3be034e7d23b7541b70da4fb"
TMP = f"{WS}/.openclaw/tmp/build"
SUBSTACK = "https://sifuyik.substack.com/subscribe"

chars = json.load(open(f"{TMP}/full.json", encoding="utf-8"))
CATS = json.loads(open(f"{PROJ}/assets/data/characters.js", encoding="utf-8")
                  .read().split("window.CATEGORIES=")[1].split(";\n")[0])
by_n = {c["n"]: c for c in chars}

# ── palette-label -> swatch tint ────────────────────────────────────────────
COLOR_WORDS = [
    ("blue-grey", "#8195a3"), ("blue gray", "#8195a3"), ("slate", "#6b7280"),
    ("charcoal", "#3b3b40"), ("ebony", "#232326"), ("black", "#232326"), ("ink", "#2b2b30"),
    ("espresso", "#4a3227"), ("chocolate", "#5b3a29"), ("cocoa", "#6b4630"), ("coffee", "#5c4033"),
    ("chestnut", "#8b4a2b"), ("russet", "#a95c33"), ("rust", "#a6522c"), ("brown", "#8a5a34"),
    ("caramel", "#c98a4b"), ("cinnamon", "#b06a3b"), ("bronze", "#b07d3f"), ("tan", "#c9a06a"),
    ("gold", "#e0b13c"), ("golden", "#e0b13c"), ("honey", "#e8b53a"), ("amber", "#d99a1f"),
    ("saffron", "#e5a92c"), ("sunflower", "#f2ca3a"), ("banana", "#f0cf4a"), ("yellow", "#f2ca3a"),
    ("cream", "#f7ecd6"), ("ivory", "#f7f0e0"), ("pearl", "#f0e9e2"),
    ("snow", "#fbfaf7"), ("white", "#fbfaf7"), ("silver", "#c9ccd2"), ("grey", "#9aa0a6"),
    ("gray", "#9aa0a6"), ("navy", "#26436b"), ("sky", "#7fc4f5"), ("azure", "#3d9df0"),
    ("blue", "#3d86f0"), ("turquoise", "#2fb8c4"), ("teal", "#1f9c9c"), ("aqua", "#56c9d6"),
    ("seafoam", "#a8e0d0"), ("mint", "#9ee6c4"), ("jade", "#3aa17e"), ("emerald", "#2e9e6b"),
    ("eucalyptus", "#7fa08c"), ("sage", "#9caf88"), ("moss", "#6b7f45"), ("olive", "#7c7a3a"),
    ("leaf", "#63a83f"), ("green", "#43a047"),
    ("blush", "#f2b8c6"), ("rose", "#e58aa0"), ("pink", "#f48fb1"),
    ("coral", "#f4736a"), ("salmon", "#ef8a72"), ("peach", "#f6b98a"), ("apricot", "#f3c08b"),
    ("cardinal", "#d23b3b"), ("ruby", "#c22a4a"), ("crimson", "#b93040"), ("burgundy", "#7d2233"),
    ("maroon", "#7a2c2c"), ("red", "#d84343"), ("tangerine", "#f59042"), ("orange", "#f08a2c"),
    ("lavender", "#b9a7e0"), ("lilac", "#c4a9dd"), ("violet", "#8b6fc4"), ("purple", "#8b6fc4"),
    ("plum", "#7a4f7a"), ("magenta", "#c73e8f"),
    ("beige", "#e4d8c3"), ("sand", "#e0cfa8"), ("khaki", "#c3b489"), ("wheat", "#e0c184"),
    ("straw", "#ddc48a"), ("bamboo", "#c2b280"), ("stone", "#b6ada2"),
]


def swatch_hex(label):
    low = label.lower()
    for word, hexv in COLOR_WORDS:
        if word in low:
            return hexv
    h = 0
    for ch in label:
        h = (h * 31 + ord(ch)) % 360
    return f"hsl({h} 32% 72%)"


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def list_join(xs):
    return " / ".join(xs)


# ── shared chrome ───────────────────────────────────────────────────────────
def head(title, desc, base=".", extra_css="", scripts=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="Sifu Yik">
<meta name="theme-color" content="#fff8ef">
<link rel="stylesheet" href="{base}/assets/css/style.css">
{extra_css}{scripts}
</head>"""


def header(active, base="."):
    def cur(name):
        return ' aria-current="page"' if active == name else ""
    return f"""<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container">
    <a class="brand" href="{base}/index.html">
      <span class="brand-mark" aria-hidden="true">Y</span>
      <span class="brand-text">Cute Animal Prompt Library
        <small>by Sifu Yik</small></span>
    </a>
    <nav class="site-nav" aria-label="Main">
      <a href="{base}/index.html#browse"{cur('browse')}>Browse</a>
      <a href="{base}/master-prompt.html"{cur('master')}>Master Prompt</a>
      <a href="{base}/about.html"{cur('about')}>About</a>
      <a class="btn btn-primary btn-sm" href="{SUBSTACK}" target="_blank" rel="noopener">Follow Sifu Yik</a>
    </nav>
  </div>
</header>
<main id="main">"""


def subscribe(compact=False):
    return f"""
<section class="subscribe" aria-labelledby="sub-h">
  <div class="subscribe-inner">
    <span class="kicker">Learn AI with Sifu Yik</span>
    <h2 id="sub-h">Want to make characters like these?</h2>
    <p>Every one of these 100 sheets started as a prompt. Sifu Yik writes about AI,
       character design and the practical craft of building with models — free, in your inbox.</p>
    <a class="btn btn-primary" href="{SUBSTACK}" target="_blank" rel="noopener">
      Subscribe on Substack
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M5 12h14M13 6l6 6-6 6"/></svg>
    </a>
    <p class="fineprint">Free to join · New articles on AI and character creation</p>
  </div>
</section>"""


def footer(base="."):
    return f"""</main>
<footer class="site-footer">
  <div class="container">
    <div>
      <h2>Cute Animal Prompt Library</h2>
      <p>A collection of 100 original cute 3D animal characters, with the character
         reference sheet prompts behind each one.</p>
      <p>Created by <strong>Sifu Yik</strong>.</p>
    </div>
    <div>
      <h2>Explore</h2>
      <a href="{base}/index.html">All 100 characters</a>
      <a href="{base}/master-prompt.html">Master prompt template</a>
      <a href="{base}/about.html">About the project</a>
    </div>
    <div>
      <h2>Learn AI</h2>
      <a href="{SUBSTACK}" target="_blank" rel="noopener">Sifu Yik on Substack</a>
      <p>Practical AI writing and tutorials.</p>
    </div>
  </div>
  <div class="footer-bottom">
    <span>&copy; {2026} Sifu Yik. Artwork and prompts all rights reserved.</span>
    <span>Built as a static showcase site.</span>
  </div>
</footer>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
</body>
</html>"""


# ── index ───────────────────────────────────────────────────────────────────
def build_index():
    featured = by_n[91]          # Maple the red panda
    hero_img = featured["full"]
    cats = "".join(
        f'<span class="trait">{esc(c["label"])}</span>' for c in CATS)

    def card(c):
        num = f'{c["n"]:02d}'
        return f"""<a class="card" href="character/{c['slug']}.html" style="--cat-color:var(--cat-{c['cat']})">
        <div class="card-media">
          <img src="{c['thumb']}" width="560" height="700" loading="lazy" decoding="async"
               alt="{esc(c['name'])} — {esc(c['species'])} character reference sheet">
          <span class="card-no" aria-hidden="true">{num}</span>
        </div>
        <div class="card-body">
          <h3 class="card-name">{esc(c['name'])}</h3>
          <p class="card-species">{esc(c['species'])}</p>
          <span class="card-cat"><span class="dot" aria-hidden="true"></span>{esc(c['catLabel'])}</span>
        </div>
      </a>"""

    cards = "\n".join(card(c) for c in chars)
    sk = "\n".join(
        '<div class="skeleton-card"><div class="sk-media"></div>'
        '<div class="sk-line"></div><div class="sk-line short"></div></div>'
        for _ in range(10))
    cat_chips = "".join(
        f'<button type="button" class="chip" data-cat="{c["id"]}" aria-pressed="false" '
        f'style="--cat-color:var(--cat-{c["id"]})"><span class="dot" aria-hidden="true"></span>'
        f'{esc(c["label"])}<span class="count">{c["count"]}</span></button>' for c in CATS)

    return head(
        "100 Cute Animal Reference Character Prompts — by Sifu Yik",
        "A showcase of 100 original cute 3D animal characters, each with its full "
        "character reference sheet prompt. Browse by category or alphabet, then copy "
        "the prompt and build your own.") + header("browse", ".") + f"""
<section class="hero">
  <div class="container hero-grid">
    <div>
      <span class="hero-eyebrow">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M12 2l2.9 6.3 6.9.8-5.1 4.7 1.4 6.8L12 17.2 5.9 20.6l1.4-6.8L2.2 9.1l6.9-.8z"/></svg>
        100 characters · prompts included
      </span>
      <h1>Meet <span class="pop">100 cute animal</span> characters, prompt and all.</h1>
      <p class="hero-lead">An original character library by Sifu Yik — playful 3D animal
        designs, each rendered as a full reference sheet with turnaround, expressions,
        palette and detail panels. Read the prompt behind any character, copy it,
        and make your own.</p>
      <div class="hero-cta">
        <a class="btn btn-primary" href="#browse">Browse the collection</a>
        <a class="btn btn-secondary" href="master-prompt.html">Get the master prompt</a>
      </div>
      <div class="hero-stats">
        <div class="hero-stat"><b>100</b><span>CHARACTER SHEETS</span></div>
        <div class="hero-stat"><b>7</b><span>COLLECTIONS</span></div>
        <div class="hero-stat"><b>100</b><span>PROMPTS TO COPY</span></div>
      </div>
    </div>
    <figure class="hero-art">
      <img src="{hero_img}" width="1120" height="1400"
           alt="Reference sheet for {esc(featured['name'])}, a cute {esc(featured['species']).lower()}: five poses, four expressions, palette and macro details.">
      <figcaption>{esc(featured['name'])} · {esc(featured['species'])} — one of the 100 sheets</figcaption>
    </figure>
  </div>
</section>

<section class="browse" id="browse" aria-labelledby="browse-h">
  <div class="container">
    <div class="browse-head">
      <h2 id="browse-h">Browse all 100</h2>
      <p class="result-count" id="resultCount" role="status" aria-live="polite"></p>
    </div>

    <div class="filter-group">
      <span class="filter-label" id="cat-label">Collection</span>
      <div class="chips" id="catChips" role="group" aria-labelledby="cat-label">
        <button type="button" class="chip" data-cat="all" aria-pressed="true" style="--cat-color:var(--accent)">
          <span class="dot" aria-hidden="true"></span>All characters<span class="count">100</span></button>
        {cat_chips}
      </div>
    </div>

    <div class="filter-group">
      <span class="filter-label" id="alpha-label">Jump to letter</span>
      <div class="alpha" id="alphaIndex" role="group" aria-labelledby="alpha-label"></div>
    </div>

    <div class="filter-group toolbar-actions">
      <button type="button" class="btn btn-secondary btn-sm" id="surpriseBtn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M4 4h16v16H4z"/><path d="M9 9h.01M15 9h.01M9 15h6"/></svg>
        Surprise me
      </button>
      <button type="button" class="btn btn-secondary btn-sm" id="resetFilters" hidden>Clear filters</button>
    </div>
  </div>
</section>

<div class="container">
  <div class="grid" id="skeleton" hidden aria-hidden="true">{sk}</div>
  <div class="grid" id="grid" role="list">{cards}</div>

  <div class="state" id="emptyState" hidden>
    <div class="state-mark" aria-hidden="true">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
    </div>
    <h3>No characters found</h3>
    <p id="emptyMsg">Try a different combination of filters.</p>
    <button type="button" class="btn btn-primary btn-sm" onclick="document.getElementById('resetFilters').click()">
      Clear filters</button>
  </div>
</div>
""" + subscribe() + footer(".") .replace(
        "</body>",
        '<script src="assets/data/characters.js"></script>\n<script src="assets/js/app.js"></script>\n</body>')


# ── character detail ────────────────────────────────────────────────────────
def build_detail(c):
    base = ".."
    nxt = by_n[c["nextN"]]
    prv = by_n[c["prevN"]]
    traits = c.get("traits") or []
    palette = c.get("palette") or []
    exps = c.get("expressions") or []
    macros = c.get("macros") or []
    tag = c.get("tagline") or []

    trait_html = "".join(f'<span class="trait">{esc(t)}</span>' for t in traits) or "<em>—</em>"
    sw_html = "".join(
        f'<span class="swatch"><i style="--sw:{swatch_hex(p)}"></i>{esc(p)}</span>' for p in palette
    ) or "<em>—</em>"
    exp_html = "".join(f"<li>{esc(e)}</li>" for e in exps) or "<li>—</li>"
    mac_html = "".join(f"<li>{esc(m)}</li>" for m in macros) or "<li>—</li>"
    tag_html = "".join(f"<span>{esc(t)}</span>" for t in tag)

    prompt_text = c["promptText"]

    return head(
        f"{c['name']} — {c['species']} | 100 Cute Animal Reference Character Prompts",
        f"{c['name']}, a cute {c['species'].lower()}. Full character reference sheet "
        f"prompt, palette, traits and detail panels. Character {c['n']} of 100 by Sifu Yik.",
        base=base) + header("browse", base) + f"""
<div class="container detail-top">
  <nav class="crumbs" aria-label="Breadcrumb">
    <a href="{base}/index.html">Collection</a>
    <span class="sep" aria-hidden="true">/</span>
    <a href="{base}/index.html?category={c['cat']}#browse">{esc(c['catLabel'])}</a>
    <span class="sep" aria-hidden="true">/</span>
    <span aria-current="page">{esc(c['name'])}</span>
  </nav>
</div>

<article class="container detail-grid">
  <figure class="detail-art">
    <img src="{base}/{c['full']}" width="1120" height="1400"
         alt="Character reference sheet for {esc(c['name'])}, a cute {esc(c['species']).lower()} — five turnaround views, four facial expressions, colour palette and four macro detail panels.">
    <figcaption>Character reference sheet · {esc(c['name'])} the {esc(c['species']).lower()}</figcaption>
  </figure>

  <div class="detail-copy" style="--cat-color:var(--cat-{c['cat']})">
    <span class="detail-no">#{c['n']:02d} of 100</span>
    <h1 class="detail-title">{esc(c['name'])}</h1>
    <p class="detail-species">{esc(c['species'])}</p>
    <span class="pill-cat"><span class="dot" aria-hidden="true"></span>{esc(c['catLabel'])}</span>
    {'<p class="tagline">' + tag_html + '</p>' if tag_html else ''}

    <dl class="facts">
      <div class="fact"><dt>Species</dt><dd>{esc(c['species'])}</dd></div>
      <div class="fact"><dt>Collection</dt><dd>{esc(c['catLabel'])}</dd></div>
      <div class="fact"><dt>Height</dt><dd>{esc(c.get('height') or '—')}</dd></div>
      <div class="fact"><dt>Personality</dt><dd><span class="trait-row">{trait_html}</span></dd></div>
      <div class="fact"><dt>Colour palette</dt><dd><span class="swatch-row">{sw_html}</span></dd></div>
      <div class="fact"><dt>Expressions</dt><dd><ul class="list-check">{exp_html}</ul></dd></div>
      <div class="fact"><dt>Detail panels</dt><dd><ul class="list-check">{mac_html}</ul></dd></div>
      {'<div class="fact"><dt>Character note</dt><dd>' + esc(c.get('bio')) + '</dd></div>' if c.get('bio') else ''}
    </dl>

    <section class="prompt-block" aria-labelledby="prompt-h">
      <div class="prompt-head">
        <h2 id="prompt-h">Reference sheet prompt</h2>
        <button type="button" class="btn btn-primary btn-sm copy-btn" data-copy-target="promptText">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="9" y="9" width="11" height="11" rx="2"/>
            <path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>
          <span data-copy-label>Copy prompt</span>
        </button>
      </div>
      <pre class="prompt-body" id="promptText" tabindex="0">{esc(prompt_text)}</pre>
    </section>
  </div>
</article>

<nav class="container pager" aria-label="Character navigation">
  <a class="prev" href="{prv['slug']}.html">
    <span class="dir">← Previous</span>
    <span class="who">{esc(prv['name'])}</span>
  </a>
  <a class="next" href="{nxt['slug']}.html">
    <span class="dir">Next →</span>
    <span class="who">{esc(nxt['name'])}</span>
  </a>
</nav>
""" + subscribe() + footer(base).replace(
        "</body>",
        '<script src="../assets/js/detail.js"></script>\n</body>')


# ── about ───────────────────────────────────────────────────────────────────
def build_about():
    cat_cards = "".join(
        f'<li style="--cat-color:var(--cat-{c["id"]})">'
        f'<a href="index.html?category={c["id"]}#browse"><span class="dot" aria-hidden="true"></span>'
        f'<strong>{esc(c["label"])}</strong> — {esc(c["desc"])} <em>({c["count"]})</em></a></li>'
        for c in CATS)

    return head(
        "About the project | 100 Cute Animal Reference Character Prompts",
        "How Sifu Yik built a library of 100 original cute 3D animal characters, "
        "and how to use the reference sheet prompts that come with them.",
        ) + header("about", ".") + f"""
<div class="container section">
  <div class="prose">
    <span class="kicker">About</span>
    <h1 style="font-size:var(--fs-h1);margin-bottom:16px">A library of 100 characters, built one prompt at a time.</h1>
    <p class="lede">This site is a showcase of an original character collection: 100 cute
      3D animal characters, each presented as a full reference sheet and each shipped with
      the exact prompt used to describe it.</p>

    <h2>What's in the collection</h2>
    <p>Every character is a single, complete presentation board. The board carries a
      five-pose turnaround (front, three-quarter, side, back and T-pose), four facial
      expressions, a labelled colour palette, a height comparison against a human
      silhouette, a short character bio, and four macro panels that zoom into materials —
      fur, scales, feathers, eyes, tails, accessories.</p>
    <p>The characters are grouped into seven collections:</p>
    <ul class="cat-list">{cat_cards}</ul>

    <h2>Why reference sheets</h2>
    <p>A single illustration gives you one moment. A reference sheet gives you a
      <em>character</em> — the same model, the same markings, the same proportions, seen from
      every angle. That consistency is what makes a design usable downstream: for animation,
      for a picture book, for a game asset, or for a series of illustrations that have to
      look like they belong together.</p>
    <p>Building a sheet also forces the design decisions to be explicit. You cannot dodge
      "what colour are the paw pads" when there is a labelled swatch on the board.</p>

    <h2>How the characters were made</h2>
    <p>Each sheet came from a written prompt following one reusable master template — the
      same structure for all 100 characters, with the character-specific detail swapped in.
      The template is published in full on the <a href="master-prompt.html">master prompt
      page</a>, along with the fill-in checklist used to prepare each one.</p>

    <h2>Using this site</h2>
    <ul>
      <li><strong>Browse</strong> — filter by collection, jump by first letter, or hit
        “Surprise me” for a random character.</li>
      <li><strong>Open a character</strong> — every card leads to a full detail page with
        the sheet, its attributes, and the complete prompt.</li>
      <li><strong>Copy a prompt</strong> — one click on any detail page, then paste it into
        whichever image model you use.</li>
      <li><strong>Adapt it</strong> — change the name, species, accessory or habitat and the
        same structure will produce a consistent sheet for your own character.</li>
    </ul>

    <div class="callout">
      <h3>On ownership and reuse</h3>
      <p>The artwork and the prompts on this site are the work of Sifu Yik. Read them, learn
        from them, and use the template to write prompts for your own original characters.
        Please don't republish the sheets or the prompt text as your own collection.</p>
    </div>

    <h2>About Sifu Yik</h2>
    <p>Sifu Yik writes about AI and the practical craft of making things with it — the
      prompts, the workflows, and the parts that actually work. This collection is a
      demonstration of that craft at scale: 100 characters, one repeatable process.</p>
  </div>
</div>
""" + subscribe() + footer(".")


# ── master prompt ───────────────────────────────────────────────────────────
def build_master():
    master_md = open(f"{WS}/.openclaw-attachments/"
                     "20260916-133715-1433e5a9-e29-Master Prompt for Cute Animal "
                     "Character Reference Sheets.md", encoding="utf-8").read()
    m = re.search(r"```text\n(.*?)\n```", master_md, re.S)
    template = m.group(1) if m else ""

    checklist = [
        ("Name", "The character's name"),
        ("Species", "Animal or creature"),
        ("Visual quirk", "The distinctive feature"),
        ("Accessory", "Signature accessory"),
        ("Habitat", "Natural habitat"),
        ("Personality", "4–5 traits"),
        ("Expressions", "4 expressions"),
        ("Palette", "4–6 colours"),
        ("Height", "In cm and ft"),
        ("Macro details", "4 design details"),
        ("Material", "Fur, scales, feathers, skin…"),
        ("Bio", "Short character description"),
    ]
    check_html = "".join(
        f'<div class="fact"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k, v in checklist)

    return head(
        "Master prompt for cute animal character reference sheets | Sifu Yik",
        "The reusable master prompt behind all 100 characters: a structured template "
        "for generating consistent 3D animal character reference sheets, plus the "
        "fill-in checklist. Free to use for your own characters.") + header("master", ".") + f"""
<div class="container section">
  <div class="prose">
    <span class="kicker">Master prompt</span>
    <h1 style="font-size:var(--fs-h1);margin-bottom:16px">The template behind all 100 sheets.</h1>
    <p class="lede">One structure, filled in 100 different ways. Copy the template, replace
      every bracketed field with your character's details, and you get a consistent
      character reference sheet instead of a one-off picture.</p>

    <div class="callout warn">
      <h2>How to use it</h2>
      <p>Paste the whole template in one go. The bracketed fields are the only parts you
        change — the surrounding structure is what keeps the sheet consistent, so don't
        trim it down if you want the turnaround, expressions and detail panels to line up.</p>
    </div>

    <h2>The master prompt</h2>
  </div>
</div>

<div class="container">
  <section class="prompt-block" aria-labelledby="mp-h" style="margin-top:0;max-width:900px">
    <div class="prompt-head">
      <h2 id="mp-h">Universal character reference sheet prompt</h2>
      <button type="button" class="btn btn-primary btn-sm copy-btn" data-copy-target="masterText">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <rect x="9" y="9" width="11" height="11" rx="2"/>
          <path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>
        <span data-copy-label>Copy template</span>
      </button>
    </div>
    <pre class="prompt-body" id="masterText" tabindex="0" style="max-height:640px">{esc(template)}</pre>
  </section>
</div>

<div class="container section">
  <div class="prose">
    <h2>Fill-in checklist</h2>
    <p>Prepare these twelve items before you write the prompt. Anything you leave vague
      shows up as inconsistency between the panels.</p>
  </div>
  <dl class="facts" style="max-width:900px">{check_html}</dl>

  <div class="prose" style="margin-top:var(--gap-xl)">
    <h2>What makes the sheet hold together</h2>
    <ul>
      <li><strong>The turnaround is described first and exactly.</strong> Five named views,
        with an explicit instruction that markings, accessories, proportions and eye line
        stay identical in every one.</li>
      <li><strong>Expressions are named, not described loosely.</strong> Four specific
        expressions, each anchored to a feeling — a labelled list beats “make it expressive”.</li>
      <li><strong>Colour is a labelled list.</strong> Naming each swatch is what stops the
        palette drifting between panels.</li>
      <li><strong>The bottom strip zooms into materials.</strong> Four macro panels, each
        with a label, so texture gets designed instead of left to chance.</li>
      <li><strong>The negative prompt is part of the prompt.</strong> Naming the failures
        up front — extra limbs, drifting colours, cropped tails, random text — is what
        keeps the board clean.</li>
    </ul>

    <div class="callout">
      <h3>Adapt it</h3>
      <p>Swap the habitat and material lines for your character's world, and keep everything
        else. The template is deliberately generic in structure and specific in its
        requirements — that combination is what makes it reusable.</p>
    </div>
  </div>
</div>
""" + subscribe() + footer(".").replace(
        "</body>", '<script src="assets/js/detail.js"></script>\n</body>')


# ── write everything ────────────────────────────────────────────────────────
os.makedirs(f"{PROJ}/character", exist_ok=True)
open(f"{PROJ}/index.html", "w", encoding="utf-8").write(build_index())
open(f"{PROJ}/about.html", "w", encoding="utf-8").write(build_about())
open(f"{PROJ}/master-prompt.html", "w", encoding="utf-8").write(build_master())
for c in chars:
    open(f"{PROJ}/character/{c['slug']}.html", "w", encoding="utf-8").write(build_detail(c))
print(f"wrote index.html, about.html, master-prompt.html + {len(chars)} character pages")
