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
assets/data/characters.js           Gallery dataset (100 records)
assets/thumbs/                      Grid images    (560 x 700)
assets/full/                        Detail images  (1120 x 1400)
assets/fonts/                       Self-hosted webfonts

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

## Credits and licensing

**Characters, artwork and prompts: Sifu Yik.**

The artwork and prompt text are published to be read, studied and learned from. You are welcome to use the template to write prompts for your own original characters. Please don't republish the character sheets or the prompt text as your own collection.

Learn AI with Sifu Yik → <https://sifuyik.substack.com/subscribe>
