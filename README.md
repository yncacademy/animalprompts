# Animal Prompt Library

A showcase of **100 original cute 3D animal characters** by **[Sifu Yik](https://sifuyik.substack.com/subscribe)** — each one presented as a full character reference sheet, and each one shipped with the exact prompt used to describe it.

---

## What's in the collection

Every character is a single, complete presentation board containing:

- a **five-pose turnaround** — front, three-quarter, side, back, T-pose
- **four facial expressions**
- a labelled **colour palette**
- a **height comparison** against a human silhouette
- a short **character bio**
- **four macro detail panels** zooming into materials — fur, scales, feathers, eyes, tails, accessories

The characters are grouped into seven collections:

| Collection | Characters |
|---|---|
| Pets & Farm | 15 |
| Forest & Meadow | 23 |
| Jungle & Savanna | 11 |
| Ocean & Reef | 21 |
| Birds & Sky | 17 |
| Reptiles & Amphibians | 10 |
| Tiny Critters | 3 |
| **Total** | **100** |

---

## Browsing features

- **Collection filter** — seven category chips, each with a live count
- **Alphabet index** — jump to a first letter; letters with no matches are disabled
- **Surprise me** — opens a random character, respecting the active filter
- **URL sync** — filters are reflected in the query string (`?category=ocean-reef`), so any filtered view is shareable and the back button works
- **Copy prompt** — one click on any character page copies its full prompt

---

## Project structure

```
index.html                          Hero + full gallery with filters
about.html                          Project story and the collections
master-prompt.html                  Reusable master prompt + fill-in checklist
character/<name>-<species>.html     100 individual character pages

assets/css/style.css                All design tokens live in :root
assets/js/app.js                    Gallery filtering, alphabet index, surprise me
assets/js/detail.js                 Copy-to-clipboard for prompts
assets/js/videos.js                 Click-to-play video logic (detail pages + featured strip)
assets/data/characters.js           Gallery dataset (100 records)
assets/thumbs/                      Grid images    (560 x 700)
assets/full/                        Detail images  (1120 x 1400)
assets/fonts/                       Self-hosted webfonts
assets/videos/<slug>.mp4            100 animated showcases (720x1280, ~5s, no audio)
assets/videos/posters/<slug>.webp   Poster frames shown before playback
assets/videos/manifest.json         Slug -> video/poster path map

source/                             Original prompt source documents
tools/                              Scripts used to generate the site
```

No CDN, no external requests — every asset ships with the site, so it renders identically offline.

---

## Running it locally

Plain static HTML. No build step and no dependencies.

```bash
# from the repository root
python3 -m http.server 8000
# open http://localhost:8000
```

Opening `index.html` straight from the filesystem also works.

---

## Using the prompts

The master prompt template is published in full at `master-prompt.html`, with the source documents in `source/`. Replace the bracketed fields with your own character's details and the same structure produces a consistent sheet.

Twelve things worth deciding before you write the prompt: name, species, visual quirk, accessory, habitat, personality traits, expressions, palette, height, macro details, material, and bio.

---

## The animated showcases

All 100 characters also have a **five-second animated showcase** (720×1280, no audio), generated from each character sheet.

- **Where**: every character page carries its clip beneath the sheet — poster frame first, plays on click. The homepage also features an eight-character strip: click any portrait to play it in the main player.
- **Delivery**: video elements are created only on click, so pages load exactly as fast as before; nothing is fetched until a visitor presses play.
- **Storage**: H.264 MP4 with `faststart`, re-encoded from the ~10 MB originals to ~2.5 MB each (246 MB total) so GitHub Pages serves them comfortably.

---

## Credits and licensing

**Characters, artwork and prompts: Sifu Yik.**

The artwork and prompt text are published to be read, studied and learned from. You are welcome to use the template to write prompts for your own original characters. Please don't republish the character sheets or the prompt text as your own collection.

Learn AI with Sifu Yik → <https://sifuyik.substack.com/subscribe>
