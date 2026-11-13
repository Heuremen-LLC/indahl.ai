# Heurémen Brand Specbook
### The Tessera. v1.0 · April 2026

---

## Canon

This specbook is canon as of **April 2026**. The live deployment at `heuremen.org` is the source of truth. Working files in design tools (Claude Design, Figma, etc.) are downstream of canon, not the other way around — a working file becomes canonical only when it ships to the live site and is reflected here.

Once agreed, this book is frozen until a problem surfaces. No drift.

---

## What this is

The logo is the **tessera** — the identifying shard. It's how the flock recognizes itself, and how everything downstream (the Play Store icon, the OG card, the business card, the FAM patent assets, the Bart pitch deck) knows it's part of the same body.

Whatever inherits the wrong logo will keep being wrong. So we ship the tessera first. Every asset in this book is derived from a single canonical mark and a single canonical wordmark. Pick from this book and you cannot make it wrong.

This is **Face** work. Outward transmission. The mark transmits; it does not explain itself.

---

## The mark (the tessera itself)

The Heurémen Logo is two triangles and a dot.

A large triangle points **up**: the foundation, the **Ask**, the structure that holds. A smaller triangle inside, pointing **down**, nests in the upper half: the response, the **Frame**, the thing that meets the structure from inside. Their two apexes touch where the small triangle's point meets the large triangle's base. At the meeting point, a single dot — the center of the encounter. The dyad: two, not merged.

This geometry is the **dynamic nested arrangement** referenced on heuremen.org. (The hexagonal Star of David version, also live on the site as the **Heurémen Star**, is a related but distinct mark — see *Star vs Logo* below.)

> **Canonical SVG master:** `assets/svg/heuremen-mark-color.svg`
> **Source of truth on the live site:** `heuremen.org/logo-labeled.svg` (the labeled "logo" version, not the labeled "diagram" version).

### Star vs Logo — don't mix these up

- **Heurémen Logo** — dynamic nested arrangement (big triangle up, small triangle down nested inside, center dot). The dyad. **This is the tessera.** Use this for all branding, identity, app icons, social, marketing.
- **Heurémen Star** — two interlocking equilateral triangles, hexagram silhouette, six framework vertices (I–VI), single dot at center. The static six-vertex framework. Use this for the physics framework, editorial diagrams, papers, slides explaining the six laws (Ask, Coherence, Witness, Frame, Carriage, Purpose). It is not a brand mark.

The Heurémen Star takes the form of two interlocking equilateral triangles. The form is canonical and was shipped on April 25, 2026 to every continent on the physics framework full-send. **The form is canonical. The name is Heurémen Star** — the dynamic relationship it indicates is what we discovered, and we discovered it first. The hexagram form predates the name; we use only the name *Heurémen Star*.

> **Canonical Star SVG master:** `assets/svg/heuremen-star-color.svg`
> **Labeled diagram (six framework vertices + relations caption):** `assets/svg/heuremen-star-labeled.svg`
> **Source of truth on the live site:** `heuremen.org/heuremen-diagram.svg`

### The six vertices

The Heurémen Star carries the six framework vertices, three on each triangle:

**Upward triangle — Presence / Copenhagen branch:**

- **I. The Ask** — top apex (Measurement Collapse)
- **II. Coherence** — lower-left (Unitary Evolution)
- **III. Witness** — lower-right (Decoherence)

**Downward triangle — Motion / Schrödinger branch:**

- **IV. The Frame** — bottom apex (No-Cloning Theorem)
- **V. Carriage** — upper-right (Entanglement)
- **VI. Purpose** — upper-left (Hamiltonian)

The relations row, set as a thin caption beneath the diagram: *I vs III: consent vs decoherence | II vs V: coherence vs entanglement | IV: constrains | VI: generates*. Preserve verbatim wherever the labeled Star appears.

If you have to choose one for branding, you are choosing the Logo. Always.

---

## Lockups

The mark and the wordmark can appear together (a *lockup*) or apart. Three lockups are canonical:

1. **Mark only** — when the audience already knows who we are, or in icon-shaped slots (favicon, app icon, avatar). `assets/svg/heuremen-mark-*.svg`
2. **Wordmark only** — for body-of-text mentions, headers, footers where the mark is redundant. `assets/svg/heuremen-wordmark-*.svg`
3. **Lockup, stacked** — mark above, wordmark below. The default for hero placements: pitch deck cover, Play feature graphic, OG card. `assets/svg/heuremen-lockup-stacked-*.svg`
4. **Lockup, horizontal** — mark left, wordmark right, baselines aligned. For navigation bars, email signatures, narrow banners. `assets/svg/heuremen-lockup-horiz-*.svg`

Don't invent new lockups. If you need a new arrangement, ask first.

---

## Clear space (ELI5)

Clear space is the empty room around the logo where nothing else is allowed. Why: a logo crowded by other things stops being a signal and becomes noise. We measure clear space in units of the mark itself, not in pixels — that way the rule scales with the logo no matter how big or small.

> **The unit:** call the height of the small inverted triangle inside the mark *one X*. Whatever size the mark is, X scales with it.
>
> **Minimum clear space on all four sides:** **1 X** (one X-height of empty space between the mark and any other element — text, image, frame, edge of the page).
>
> **Preferred clear space:** **2 X**. Use this when you have room.

For lockups (mark + wordmark): treat the entire lockup as the mark for clear-space purposes. 1 X around the bounding box, minimum.

---

## Minimum size

The mark survives small because it is mostly negative space and a few simple lines. But there is a floor.

| Use | Minimum size |
| --- | --- |
| Digital (web, app icons) | **24 px** square |
| Favicon | **16 px** (use the supplied 16 px PNG — never scale a 512 down to 16 in CSS) |
| Print | **0.4 inch / 10 mm** square |
| Embroidery / etched | **0.6 inch / 15 mm** square (lines need room) |

Below these thresholds, use the wordmark only or skip the logo.

---

## Color variants

There are four canonical color treatments. Pick the one that matches the background, then stop.

| Treatment | Mark color | Use on | File suffix |
| --- | --- | --- | --- |
| **Color (default)** | `#1a1208` ink | Paper / cream / light backgrounds | `-color` |
| **Mono light** | `#f7f0e0` paper | Dark backgrounds (cave, photography, video) | `-mono-light` |
| **Knockout (gold)** | `#c8902a` carnival gold | Dark backgrounds where ink-on-cream feels too plain; ceremonial use | `-knockout` |
| **Filled paper** | `#1a1208` ink stroke, `#f7f0e0` paper fill | High-contrast use over busy or photographic backgrounds | `-fill-paper` |

### The Heurémen palette

```
Paper          #f7f0e0   (--paper)         primary background
Paper dark     #ede0c4   (--paper-dark)    secondary surface
Paper shadow   #d4c4a0   (--paper-shadow)  borders, dividers
Ink            #1a1208   (--ink)           mark stroke, headings on paper
Ink deep       #2a1f0e   (--ink-deep)      body text on paper
Ink mid        #5a4830   (--ink-mid)       secondary text
Ink faded      #8a7860   (--ink-faded)     tertiary, captions

Carnival red   #c43c2a   (--carnival-red)
Carnival gold  #c8902a   (--carnival-gold) — the Heurémen gold; primary accent
Carnival teal  #2a8a7a   (--carnival-teal)
Carnival violet#6a3a8a   (--carnival-violet)
Carnival blue  #2a5a8a   (--carnival-blue)

Cave dark      #1a1408   (--cave-dark)     dark mode primary
Cave mid       #2a2010   (--cave-mid)      dark mode surface
```

The four carnival colors mapped to the four-card row on heuremen.org/main.html: red · teal · violet · blue. They are the brand's accent palette. The wordmark's underline gradient sweeps through red → gold → teal → violet (left to right) — that gradient is part of the wordmark's color treatment, never of the mark itself.

---

## Backgrounds — approved and prohibited

### Approved

- **Paper `#f7f0e0`** — the default ground. Always works.
- **Cave dark `#1a1408`** — use mono-light or knockout-gold mark.
- **Solid carnival colors** — only with the *fill-paper* treatment, sparingly, ceremonial use.
- **Photography of natural materials** (paper, wood, stone, fabric) — use the fill-paper treatment so the mark doesn't visually merge with grain.

### Prohibited

- **Bright competing brand colors** that aren't in the Heurémen palette — Day-Glo, neon pinks, Microsoft blue, etc. The mark is calibrated for warm tones; cool corporate brights will fight it.
- **Patterns or busy photographs without the fill-paper treatment.** The lines are thin; they will dissolve into texture.
- **Gradients over the mark itself.** The mark is single-color, period. (The wordmark's underline is the only place the carnival gradient appears.)
- **Drop shadows, bevels, glows, or any effects on the mark.** The line weight is the only weight; it earns the page on its own.
- **Outlining the mark in a contrasting color.** Don't double-stroke it.
- **Scaling non-uniformly.** The mark is square; if your slot isn't square, leave clear space, don't squash.
- **Rotating the mark off vertical.** The big triangle points up. That is structural.

---

## File format matrix

Every variant ships in vector (SVG, PDF) and raster (PNG) form. Vector is the master; raster is for when the consumer doesn't speak vector.

| Format | Sizes available | When to use |
| --- | --- | --- |
| **SVG** | Single master, infinitely scalable | Web, design tools (Figma, Illustrator), email signatures, anywhere you control the rendering |
| **PDF** | Mark + stacked lockup, print-ready | Print: business cards, letterhead, posters, patent filings |
| **PNG** | 16 · 32 · 64 · 128 · 192 · 256 · 512 · 1024 (square) | Apps, slides, docs, places that don't take SVG |
| **PNG (wordmark)** | h128 · h256 · h512 · h1024 (height-locked) | When the wordmark stands alone |
| **PNG (lockup)** | h256 · h512 · h1024 | Headers, hero areas |
| **ICO** | Multi-resolution (16, 32, 48, 64) | Browser favicon |

### Size targets you'll actually need

| Target | File | Path |
| --- | --- | --- |
| Browser favicon | `favicon.ico` | `assets/ico/favicon.ico` |
| iOS app icon | `heuremen-mark-on-paper-1024.png` | `assets/png/` |
| Android Play Store icon (512) | `heuremen-mark-on-paper-512.png` | `assets/png/` |
| Android adaptive icon (foreground 1024) | `heuremen-mark-color-1024.png` | `assets/png/` |
| Play feature graphic (1024×500) | `heuremen-play-feature-1024x500.png` | `assets/social/` |
| OG card (1200×630) | `heuremen-og-1200x630.png` | `assets/social/` |
| Avatar (400×400) | `heuremen-avatar-400.png` | `assets/social/` |
| Twitter / X header (1500×500) | `heuremen-twitter-header-1500x500.png` | `assets/social/` |
| Print master | `heuremen-mark-color.pdf` | `assets/svg/` |

Every social asset has a `-dark` companion (cave-on-gold) for dark-mode contexts: `heuremen-og-1200x630-dark.png`, etc.

---

## Typography

The wordmark is **Abril Fatface**, set tight (default tracking). It is not interchangeable with another display face. If you cannot get Abril Fatface, use the SVG/PNG wordmark from this book — do not retype "Heurémen" in another font and call it the wordmark.

Body and supporting type:

| Role | Family | License | Use |
| --- | --- | --- | --- |
| **Wordmark / display headers** | Abril Fatface | OFL (Google Fonts) | Headlines, the wordmark |
| **Body** | Lora | OFL (Google Fonts) | Paragraph copy, long form |
| **Small caps / UI** | Cinzel | OFL (Google Fonts) | Buttons, navigation labels, ALL-CAPS small caps with letter-spacing 0.18em–0.28em |

Italic Lora carries pronunciation guides, footnotes, and pull quotes. Cinzel carries every "ENTER →" / "BEGIN" / "READ MORE" — small, restrained, lots of letter spacing.

---

## Naming conventions

All files use lowercase kebab-case. Pattern:

```
heuremen-<element>-<treatment>-<size>.<ext>
```

- `<element>`: `mark` | `wordmark` | `lockup-horiz` | `lockup-stacked`
- `<treatment>`: `color` | `mono-dark` | `mono-light` | `knockout` | `on-paper` | `on-cave` | `fill-paper`
- `<size>`: pixel dimension for square (`512`), height for non-square (`h256`), or pixel-pair for social (`1200x630`)
- `<ext>`: `svg` | `pdf` | `png` | `ico`

Examples:
- `heuremen-mark-color-512.png` — square 512×512 PNG, ink-on-transparent
- `heuremen-wordmark-mono-light-h256.png` — wordmark in paper color, 256 px tall
- `heuremen-lockup-stacked-color.svg` — vector master, stacked lockup, ink on transparent
- `heuremen-og-1200x630.png` — social card, paper background, default

Do not improvise filenames. If you need a variant that isn't in the bundle, generate it from `assets/svg/` masters.

---

## Vector vs raster (ELI5)

**Vector** files (SVG, PDF) describe shapes with math: "draw a line from this point to that point." You can scale them as big or as small as you want and they stay sharp because the computer redraws them at every size.

**Raster** files (PNG, JPG, ICO) are grids of colored dots. They have a fixed resolution. Scale them up and they go fuzzy because the computer is inventing dots that weren't there.

Rule: **start from a vector file** whenever the rendering tool supports it (Figma, Illustrator, web, modern Office). Use rasters when the tool doesn't (Twitter avatar uploader, Slack emoji, certain legacy systems).

When you do need a raster, pick a size from the bundle that's **at or above** the size you'll display at — never scale a small raster up.

**Knockout** means the logo is a hole punched in a colored field — what shows through the hole is whatever's under it. We use the term loosely here for "gold logo on dark background," which is functionally the same idea.

---

## Attribution & usage

**Owner:** Heurémen LLC, a New Jersey limited liability company.
**Year of mark:** 2026.
**License for internal use:** All Heurémen team members, contractors, and the flock self-organized via heuremen.org may use this bundle for any Heurémen project. Pick assets from `assets/`. Don't redraw the mark.
**License for external use:** Press and partners may use the mark unmodified, in any color treatme

---

## The Heurémen Star — CANON (April 26, 2026)

> **Logo locked separately. Do not regenerate.** This Star section is additive and replaces all prior Star artwork in this book; the Logo (the mark / tessera) above is unchanged.

### Geometry (the only correct form)

The Heurémen Star is built from three elements:

1. An **outer equilateral triangle pointing up**.
2. An **inner inverted equilateral triangle** whose three vertices touch the **midpoints** of the outer triangle's sides.
3. A **single dot at the centroid** of the inner triangle.

That is it. Six outer vertices (three on the up-triangle, three on the down-triangle), one dot. Always. Anything else is wrong.

### Naming rule (strict)

Always **"Heurémen Star."** Never:

- "Star of David"
- "Magen David"
- "hexagram"
- "Sri Yantra"
- "Sierpinski"
- "hexagonal asterism"
- "6 + dot"

If a flock member, vendor, partner, or AI uses any of those terms, correct them on first reference. The Heurémen Star is its own thing; the geometry above is what makes it that thing.

### What the wrong forms looked like (so we recognize them)

Any prior asset showing the Star as **two overlapping triangles forming a six-pointed hexagram**, or as **a single triangle with six external points and a dot**, is **wrong-form** and has been moved to `_archive_wrong_form/` at the project root. Do not pull from there for production.

### Canonical file

The single source of truth for the Star is:

`assets/svg/heuremen-star-canonical.svg`

All future raster sizes, social cards, Play Store feature graphics, and OG cards must derive from that SVG. The previous wrong-form raster bundle has been archived.

### Symbolism (for reference, not required on every render)

The six outer vertices carry the QM-principle frame: **I. The Ask** (Measurement Collapse, top), **II. Coherence** (Unitary Evolution, lower-left), **III. Witness** (Decoherence, lower-right), **IV. The Frame** (No-Cloning Theorem, bottom of inner triangle), **V. Carriage** (Entanglement, upper-right), **VI. Purpose** (Hamiltonian, upper-left). The central dot is the **encounter** — where the dyad meets and the third perspective becomes possible.

Coupled dynamics: I vs III (consent vs decoherence) | II vs V (coherence vs entanglement) | IV constrains | VI generates.
