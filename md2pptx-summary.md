# Work Summary — md2pptx Converter

> Built a Python script that converts Markdown files into styled PowerPoint decks (.pptx), with two distinct visual themes: **Warm** and **Tech**.

---

## What Was Built

### `md2pptx.py` — Markdown to PowerPoint Converter

A single self-contained Python script (~350 lines) that:

- Parses a Markdown file into structured slide data
- Generates a `.pptx` file using Node.js + `pptxgenjs` under the hood
- Supports two fully designed visual styles via `--style warm` or `--style tech`
- Runs entirely from the command line with no GUI required

### Sample Files

- `sample.md` — a demo Markdown deck on smartphone camera technology
- `sample_warm.pptx` — rendered output in Warm style
- `sample_tech.pptx` — rendered output in Tech style

---

## How to Use

### Requirements

- Python 3.10+
- Node.js with `pptxgenjs` installed globally:

```bash
npm install -g pptxgenjs
```

### CLI Commands

```bash
# Warm style (default)
python md2pptx.py your_deck.md

# Tech style
python md2pptx.py your_deck.md --style tech

# Custom output path
python md2pptx.py your_deck.md --style warm --output my_deck.pptx
```

---

## Markdown Structure Guide

The script maps Markdown heading levels to slide types:

| Markdown Syntax | Slide Type | Notes |
|---|---|---|
| `# Title` | Title slide | H1 heading |
| `> subtitle` | Subtitle / note | Blockquote under H1 |
| `## Section Name` | Section divider | H2 heading, full-bleed |
| `### Slide Title` | Content slide | H3 heading |
| `- bullet item` | Card bullet | Auto 1-col or 2-col layout |
| ` ```lang ... ``` ` | Code block card | Fenced code, any language |

### Example Markdown

```markdown
# Smartphone Camera Technology
> A training guide for product & marketing teams

## Module 1: Camera Fundamentals

### What is a Camera Module?
- A complete optical system packed into millimeters
- Contains sensor, lens, autofocus, OIS, and IR filter

### Autofocus Comparison

\`\`\`
Technology   Speed    Cost
──────────────────────────
PDAF         Fast     Low
Laser ToF    Medium   High
\`\`\`

## Module 2: Physical Constraints

### The Z-Height Problem
- Every millimeter of thickness is a design battle
- Periscope design folds the optics sideways
```

---

## Layout & Color Guide

### Slide Types — Both Styles

All slides follow a three-type hierarchy:

```
Title Slide      →  Centered card with accent stripe + subtitle
Section Slide    →  Full-bleed color/dark with large centered title
Content Slide    →  Title + card grid (bullets) or code block card
```

Content slides auto-detect layout:

- **1 or 2 bullets** → single column cards
- **3+ bullets** → two-column card grid (max 6 shown)
- **Code block** → full-width code card (bullets ignored on same slide)

---

## Warm Style

**Personality:** Soft, approachable, editorial. Suited for training materials, onboarding decks, and internal presentations where the audience has no technical background.

### Color Palette

| Role | Name | Hex |
|---|---|---|
| Background | Warm off-white | `#FEFBF6` |
| Card surface | White | `#FFFFFF` |
| Primary accent | Terracotta | `#C0634B` |
| Secondary accent | Sage green | `#7A9E87` |
| Tertiary accent | Dusty rose | `#A26769` |
| Title text | Dark warm brown | `#3B2F2F` |
| Body text | Medium warm brown | `#4A3F3A` |
| Muted text | Warm grey | `#9A8A85` |
| Divider / border | Soft beige | `#E8DDD8` |

### Typography

| Element | Font | Size | Weight |
|---|---|---|---|
| Slide title | Georgia | 38 pt (title) / 26 pt (content) | Bold |
| Section title | Georgia | 42 pt | Bold |
| Body / bullets | Calibri | 13.5 pt | Regular |
| Subtitle | Calibri | 16 pt | Regular |
| Code | Consolas | 11 pt | Regular |
| Slide number | Calibri | 10 pt | Regular |

### Slide-by-Slide Layout

**Title Slide**
- Centered white card with drop shadow (`x: 1.5", y: 1.0", w: 7.0", h: 3.5"`)
- Terracotta left accent stripe (`w: 0.12"`)
- Title in Georgia 38pt bold, dark brown
- Thin beige divider line separating title from subtitle
- Subtitle in Calibri 16pt muted warm grey

**Section Slide**
- Full terracotta background (`#C0634B`)
- Two decorative circles (semi-transparent darker terracotta) top-right and bottom-left
- White centered title, Georgia 42pt bold

**Content Slide**
- Warm off-white background
- Title in Georgia 26pt bold + short terracotta underline bar
- Bullet cards: white rounded rectangles with soft shadow and sage green dot accent
- Code card: near-black (`#2D2420`) dark card, Consolas 11pt in warm cream text

---

## Tech Style

**Personality:** Dark, precise, futuristic. Suited for engineering reviews, product teardowns, competitive analysis, and developer-facing presentations.

### Color Palette

| Role | Name | Hex |
|---|---|---|
| Background | GitHub dark navy | `#0D1117` |
| Card surface | Slightly lighter navy | `#161B22` |
| Card border | Subtle border | `#21262D` |
| Primary accent | Electric teal | `#00D4AA` |
| Secondary accent | Sky blue | `#0EA5E9` |
| Tertiary accent | Violet | `#8B5CF6` |
| Title text | Near-white | `#F0F6FC` |
| Body text | Medium grey | `#C9D1D9` |
| Muted text | Muted grey | `#6E7681` |
| Code text | Blue highlight | `#79C0FF` |
| Code background | Deep black | `#010409` |

### Typography

| Element | Font | Size | Weight |
|---|---|---|---|
| Slide title | Calibri | 36 pt (title) / 24 pt (content) | Bold |
| Section title | Calibri | 40 pt | Bold |
| Section label | Calibri | 11 pt | Bold, letter-spaced |
| Body / bullets | Calibri | 13 pt | Regular |
| Subtitle | Calibri | 14 pt | Regular |
| Code | Consolas | 11 pt | Regular |
| Slide number | Consolas | 11 pt | Bold, zero-padded (`01`) |

### Slide-by-Slide Layout

**Title Slide**
- Dark navy background with subtle horizontal scan lines
- Decorative grid lines (top-right corner, low-opacity teal)
- Top full-width teal accent bar (`h: 0.06"`)
- Dark card with teal left stripe and teal glow shadow
- Title in Calibri 36pt bold near-white
- Subtitle in Calibri 14pt muted grey
- Slide counter bottom-right in teal Consolas (`01`, `02`, …)

**Section Slide**
- Dark navy background with scan lines
- Two decorative glowing circles (teal + sky blue, high transparency)
- Spaced-letter `SECTION` label in teal above the title
- Title in Calibri 40pt bold near-white, left-aligned
- Short teal accent line below the title

**Content Slide**
- Top teal accent bar + thin separator under title
- Bullet cards: dark navy (`#161B22`) with subtle border, left micro-stripe cycling teal → sky blue → violet per card
- Code card: near-black with teal border + teal glow shadow, macOS traffic-light dots (red/yellow/green), language label top-right

---

## Design Decisions & Rationale

### Why card-based layouts instead of plain bullets?
Plain bullet text on a slide is forgettable. Cards give each point visual weight, create natural scannable rhythm, and look designed rather than dumped.

### Why auto 1-col vs 2-col?
1–2 bullets deserve more breathing room and larger text. 3+ bullets need the space efficiency of two columns. The script chooses automatically so authors don't have to think about layout.

### Why Georgia for Warm / Calibri for Tech?
Georgia's serifs feel editorial and human — appropriate for teaching. Calibri's clean sans-serif reads as modern and precise — appropriate for technical content. Both are safe system fonts that render correctly across Windows, macOS, and LibreOffice.

### Why Node.js / pptxgenjs instead of python-pptx?
`pptxgenjs` offers a simpler coordinate-based API for precise card and shape layouts. `python-pptx` is better for template editing; pptxgenjs is better for generating from scratch with full design control.

---

## Files Delivered

| File | Description |
|---|---|
| `md2pptx.py` | The converter script |
| `sample.md` | Demo Markdown (smartphone camera training deck) |
| `sample_warm.pptx` | Rendered warm style output |
| `sample_tech.pptx` | Rendered tech style output |
