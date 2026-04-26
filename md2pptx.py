#!/usr/bin/env python3
"""
md2pptx.py — Convert Markdown files to PowerPoint (.pptx)

Two styles:
  --style warm        Soft, warm tones with rounded cards (default)
  --style tech        Dark tech aesthetic with accent colors

Usage:
  python md2pptx.py input.md
  python md2pptx.py input.md --style tech
  python md2pptx.py input.md --style warm --output my_deck.pptx
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap


# ─────────────────────────────────────────────────────────────────────────────
#  Markdown Parser
# ─────────────────────────────────────────────────────────────────────────────

def parse_markdown(md_text: str) -> list[dict]:
    """
    Parse a Markdown file into a list of slide dicts.

    Slide boundaries:
      - H1 (#)  → Title slide
      - H2 (##) → Section divider slide
      - H3 (###) → Content slide

    Returns a list of:
      { "type": "title"|"section"|"content",
        "title": str,
        "subtitle": str | None,      # for title slides
        "bullets": [str, ...],       # for content slides
        "code": str | None,          # fenced code block
        "note": str | None }         # blockquote becomes speaker note
    """
    slides = []
    lines = md_text.splitlines()

    current_slide = None
    in_code = False
    code_buf = []
    code_lang = ""

    def flush():
        nonlocal current_slide
        if current_slide:
            slides.append(current_slide)
        current_slide = None

    for line in lines:
        # ── fenced code block ──────────────────────────────────────────────
        if line.startswith("```"):
            if not in_code:
                in_code = True
                code_lang = line[3:].strip()
                code_buf = []
            else:
                in_code = False
                if current_slide is not None:
                    current_slide["code"] = "\n".join(code_buf)
                    current_slide["code_lang"] = code_lang
            continue

        if in_code:
            code_buf.append(line)
            continue

        # ── H1: title slide ────────────────────────────────────────────────
        if line.startswith("# ") and not line.startswith("## "):
            flush()
            current_slide = {
                "type": "title",
                "title": line[2:].strip(),
                "subtitle": None,
                "bullets": [],
                "code": None,
                "code_lang": "",
                "note": None,
            }
            continue

        # ── H2: section slide ──────────────────────────────────────────────
        if line.startswith("## ") and not line.startswith("### "):
            flush()
            current_slide = {
                "type": "section",
                "title": line[3:].strip(),
                "subtitle": None,
                "bullets": [],
                "code": None,
                "code_lang": "",
                "note": None,
            }
            continue

        # ── H3: content slide ──────────────────────────────────────────────
        if line.startswith("### "):
            flush()
            current_slide = {
                "type": "content",
                "title": line[4:].strip(),
                "subtitle": None,
                "bullets": [],
                "code": None,
                "code_lang": "",
                "note": None,
            }
            continue

        if current_slide is None:
            continue

        # ── blockquote → speaker note / subtitle ──────────────────────────
        if line.startswith("> "):
            text = line[2:].strip()
            if current_slide["type"] == "title" and not current_slide["subtitle"]:
                current_slide["subtitle"] = text
            else:
                current_slide["note"] = text
            continue

        # ── horizontal rule → ignored ──────────────────────────────────────
        if re.match(r"^[-*_]{3,}$", line.strip()):
            continue

        # ── bullet / list ─────────────────────────────────────────────────
        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)", line)
        if m:
            indent = len(m.group(1))
            text = m.group(3).strip()
            # Strip inline markdown bold/italic/code
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
            text = re.sub(r"\*(.+?)\*", r"\1", text)
            text = re.sub(r"`(.+?)`", r"\1", text)
            current_slide["bullets"].append({"text": text, "level": indent // 2})
            continue

        # ── plain paragraph ────────────────────────────────────────────────
        stripped = line.strip()
        if stripped:
            stripped = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped)
            stripped = re.sub(r"\*(.+?)\*", r"\1", stripped)
            stripped = re.sub(r"`(.+?)`", r"\1", stripped)
            if current_slide["type"] == "title" and not current_slide["subtitle"]:
                current_slide["subtitle"] = stripped
            else:
                current_slide["bullets"].append({"text": stripped, "level": 0})

    flush()
    return slides


# ─────────────────────────────────────────────────────────────────────────────
#  Node.js / pptxgenjs generator  (called via subprocess)
# ─────────────────────────────────────────────────────────────────────────────

WARM_TEMPLATE = r"""
const pptxgen = require('pptxgenjs');

// ── Warm style ─────────────────────────────────────────────────────────────
// Palette: warm cream bg, terracotta accent, sage green, dusty rose
const C = {
  bg:       'FEFBF6',   // warm off-white background
  card:     'FFFFFF',   // card surface
  accent1:  'C0634B',   // terracotta
  accent2:  '7A9E87',   // sage green
  accent3:  'A26769',   // dusty rose
  titleFg:  '3B2F2F',   // dark warm brown (titles)
  bodyFg:   '4A3F3A',   // medium warm brown (body)
  mutedFg:  '9A8A85',   // muted warm grey
  divider:  'E8DDD8',   // soft divider
};

const FONT_HEAD = 'Georgia';
const FONT_BODY = 'Calibri';

const slides = SLIDES_JSON;

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';

slides.forEach((s, idx) => {
  let slide = pres.addSlide();
  slide.background = { color: C.bg };

  // ── Title slide ────────────────────────────────────────────────────────
  if (s.type === 'title') {
    // Centered card
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 1.5, y: 1.0, w: 7.0, h: 3.5,
      fill: { color: C.card },
      shadow: { type: 'outer', color: '8B7355', blur: 18, offset: 4, angle: 135, opacity: 0.12 },
      line: { color: C.divider, width: 1 },
    });
    // Accent bar (left edge)
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 1.5, y: 1.0, w: 0.12, h: 3.5,
      fill: { color: C.accent1 },
    });
    // Title
    slide.addText(s.title, {
      x: 1.72, y: 1.3, w: 6.6, h: 1.4,
      fontFace: FONT_HEAD, fontSize: 38, bold: true,
      color: C.titleFg, valign: 'middle', margin: 0,
    });
    // Divider line
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 1.72, y: 2.78, w: 5.5, h: 0.02,
      fill: { color: C.divider },
    });
    // Subtitle
    if (s.subtitle) {
      slide.addText(s.subtitle, {
        x: 1.72, y: 2.88, w: 6.6, h: 1.0,
        fontFace: FONT_BODY, fontSize: 16, color: C.mutedFg,
        valign: 'top', margin: 0,
      });
    }
    // Slide number (bottom right)
    slide.addText(`${idx + 1}`, {
      x: 9.0, y: 5.2, w: 0.6, h: 0.3,
      fontFace: FONT_BODY, fontSize: 10, color: C.mutedFg,
      align: 'right', margin: 0,
    });
  }

  // ── Section slide ──────────────────────────────────────────────────────
  else if (s.type === 'section') {
    // Full-width accent stripe
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: 10, h: 5.625,
      fill: { color: C.accent1 },
    });
    // Decorative circle
    slide.addShape(pres.shapes.OVAL, {
      x: 7.0, y: -1.5, w: 5, h: 5,
      fill: { color: 'C8745E', transparency: 60 },
      line: { color: 'C8745E', width: 0 },
    });
    slide.addShape(pres.shapes.OVAL, {
      x: -1.0, y: 3.0, w: 4, h: 4,
      fill: { color: 'A8543E', transparency: 70 },
      line: { color: 'A8543E', width: 0 },
    });
    slide.addText(s.title, {
      x: 1.0, y: 1.8, w: 8.0, h: 2.0,
      fontFace: FONT_HEAD, fontSize: 42, bold: true,
      color: 'FFFFFF', align: 'center', valign: 'middle', margin: 0,
    });
  }

  // ── Content slide ──────────────────────────────────────────────────────
  else {
    const hasBullets = s.bullets && s.bullets.length > 0;
    const hasCode    = !!s.code;

    // Title area
    slide.addText(s.title, {
      x: 0.5, y: 0.25, w: 9.0, h: 0.7,
      fontFace: FONT_HEAD, fontSize: 26, bold: true,
      color: C.titleFg, valign: 'middle', margin: 0,
    });
    // Title underline
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y: 1.0, w: 1.5, h: 0.05,
      fill: { color: C.accent1 },
    });

    if (hasCode) {
      // Code card
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.5, y: 1.2, w: 9.0, h: 3.8,
        fill: { color: '2D2420' },
        shadow: { type: 'outer', color: '8B7355', blur: 12, offset: 3, angle: 135, opacity: 0.15 },
      });
      // Lang badge
      if (s.code_lang) {
        slide.addShape(pres.shapes.RECTANGLE, {
          x: 0.5, y: 1.2, w: 1.0, h: 0.28,
          fill: { color: C.accent1 },
        });
        slide.addText(s.code_lang.toUpperCase(), {
          x: 0.52, y: 1.2, w: 0.96, h: 0.28,
          fontFace: FONT_BODY, fontSize: 9, bold: true,
          color: 'FFFFFF', align: 'center', valign: 'middle', margin: 0,
        });
      }
      slide.addText(s.code, {
        x: 0.7, y: 1.55, w: 8.6, h: 3.3,
        fontFace: 'Consolas', fontSize: 11,
        color: 'D4C5B2', valign: 'top', margin: 0,
      });
    } else if (hasBullets) {
      // Cards for bullets
      const bullets = s.bullets;
      const MAX_CARDS = 5;
      const CARD_COLS = bullets.length >= 3 ? 2 : 1;
      const shown = bullets.slice(0, MAX_CARDS);
      const cardW = CARD_COLS === 2 ? 4.35 : 9.0;
      const startX = 0.5;
      const startY = 1.25;
      const cardH = CARD_COLS === 2
        ? Math.min(1.0, (4.0 / Math.ceil(shown.length / 2)))
        : Math.min(0.75, (4.0 / shown.length));
      const gapX = 0.3;
      const gapY = 0.18;

      shown.forEach((b, i) => {
        const col  = CARD_COLS === 2 ? i % 2 : 0;
        const row  = CARD_COLS === 2 ? Math.floor(i / 2) : i;
        const cx   = startX + col * (cardW + gapX);
        const cy   = startY + row * (cardH + gapY);

        // Card bg
        slide.addShape(pres.shapes.RECTANGLE, {
          x: cx, y: cy, w: cardW, h: cardH,
          fill: { color: C.card },
          shadow: { type: 'outer', color: '8B7355', blur: 8, offset: 2, angle: 135, opacity: 0.10 },
          line: { color: C.divider, width: 1 },
        });
        // Accent dot
        slide.addShape(pres.shapes.OVAL, {
          x: cx + 0.18, y: cy + cardH / 2 - 0.08, w: 0.16, h: 0.16,
          fill: { color: C.accent2 },
          line: { color: C.accent2, width: 0 },
        });
        // Bullet text
        slide.addText(b.text, {
          x: cx + 0.44, y: cy, w: cardW - 0.54, h: cardH,
          fontFace: FONT_BODY, fontSize: 13.5, color: C.bodyFg,
          valign: 'middle', margin: 0,
        });
      });
    }

    // Slide number
    slide.addText(`${idx + 1}`, {
      x: 9.0, y: 5.2, w: 0.6, h: 0.3,
      fontFace: FONT_BODY, fontSize: 10, color: C.mutedFg,
      align: 'right', margin: 0,
    });
  }
});

pres.writeFile({ fileName: OUTPUT_PATH }).then(() => {
  console.log('OK:' + OUTPUT_PATH);
}).catch(err => {
  console.error('ERROR:' + err.message);
  process.exit(1);
});
"""

TECH_TEMPLATE = r"""
const pptxgen = require('pptxgenjs');

// ── Tech style ─────────────────────────────────────────────────────────────
// Palette: deep navy bg, electric teal accent, cyan highlights
const C = {
  bg:       '0D1117',   // GitHub-dark navy
  card:     '161B22',   // slightly lighter card
  border:   '21262D',   // subtle card border
  accent1:  '00D4AA',   // electric teal (primary)
  accent2:  '0EA5E9',   // sky blue
  accent3:  '8B5CF6',   // violet
  titleFg:  'F0F6FC',   // near-white titles
  bodyFg:   'C9D1D9',   // medium grey body
  mutedFg:  '6E7681',   // muted grey
  codeBg:   '0D1117',   // same as bg for seamless code
  codeText: '79C0FF',   // blue-ish code text
};

const FONT_HEAD = 'Calibri';
const FONT_BODY = 'Calibri';
const FONT_MONO = 'Consolas';

const slides = SLIDES_JSON;

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';

// Helper: horizontal scan line pattern (decorative)
function addScanLines(slide) {
  for (let i = 0; i < 8; i++) {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: i * 0.72, w: 10, h: 0.36,
      fill: { color: 'FFFFFF', transparency: 98 },
      line: { color: '000000', width: 0 },
    });
  }
}

slides.forEach((s, idx) => {
  let slide = pres.addSlide();
  slide.background = { color: C.bg };
  addScanLines(slide);

  // ── Title slide ────────────────────────────────────────────────────────
  if (s.type === 'title') {
    // Top accent bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: 10, h: 0.06,
      fill: { color: C.accent1 },
    });
    // Decorative grid lines (top-right corner)
    for (let i = 1; i <= 4; i++) {
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 10 - i * 0.35, y: 0, w: 0.01, h: 2.5,
        fill: { color: C.accent1, transparency: 85 },
      });
    }
    for (let i = 1; i <= 4; i++) {
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 7, y: i * 0.55, w: 2.8, h: 0.01,
        fill: { color: C.accent1, transparency: 85 },
      });
    }
    // Card
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.6, y: 1.2, w: 7.5, h: 3.2,
      fill: { color: C.card },
      line: { color: C.border, width: 1 },
      shadow: { type: 'outer', color: '00D4AA', blur: 20, offset: 0, angle: 135, opacity: 0.15 },
    });
    // Accent left stripe
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.6, y: 1.2, w: 0.08, h: 3.2,
      fill: { color: C.accent1 },
    });
    // Title
    slide.addText(s.title, {
      x: 0.85, y: 1.4, w: 7.1, h: 1.5,
      fontFace: FONT_HEAD, fontSize: 36, bold: true,
      color: C.titleFg, valign: 'middle', margin: 0,
    });
    // Divider
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.85, y: 2.95, w: 5.0, h: 0.02,
      fill: { color: C.accent1, transparency: 40 },
    });
    // Subtitle
    if (s.subtitle) {
      slide.addText(s.subtitle, {
        x: 0.85, y: 3.05, w: 7.1, h: 1.0,
        fontFace: FONT_BODY, fontSize: 14, color: C.mutedFg,
        valign: 'top', margin: 0,
      });
    }
    // Slide counter
    slide.addText(`${(idx + 1).toString().padStart(2, '0')}`, {
      x: 9.0, y: 5.15, w: 0.7, h: 0.35,
      fontFace: FONT_MONO, fontSize: 11, bold: true,
      color: C.accent1, align: 'right', margin: 0,
    });
  }

  // ── Section slide ──────────────────────────────────────────────────────
  else if (s.type === 'section') {
    // Full dark bg with accent glow circle
    slide.addShape(pres.shapes.OVAL, {
      x: 5.5, y: -1.5, w: 7.0, h: 7.0,
      fill: { color: '00D4AA', transparency: 92 },
      line: { color: '00D4AA', width: 0 },
    });
    slide.addShape(pres.shapes.OVAL, {
      x: -1.5, y: 2.5, w: 4.0, h: 4.0,
      fill: { color: '0EA5E9', transparency: 94 },
      line: { color: '0EA5E9', width: 0 },
    });
    // Top bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: 10, h: 0.06,
      fill: { color: C.accent1 },
    });
    // Section label
    slide.addText('SECTION', {
      x: 0.6, y: 1.6, w: 8.8, h: 0.4,
      fontFace: FONT_MONO, fontSize: 11, bold: true,
      color: C.accent1, charSpacing: 8, margin: 0,
    });
    slide.addText(s.title, {
      x: 0.6, y: 2.1, w: 8.8, h: 1.8,
      fontFace: FONT_HEAD, fontSize: 40, bold: true,
      color: C.titleFg, valign: 'middle', margin: 0,
    });
    // Bottom accent line
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.6, y: 3.95, w: 2.0, h: 0.06,
      fill: { color: C.accent1 },
    });
  }

  // ── Content slide ──────────────────────────────────────────────────────
  else {
    const hasBullets = s.bullets && s.bullets.length > 0;
    const hasCode    = !!s.code;

    // Top accent bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 0, w: 10, h: 0.05,
      fill: { color: C.accent1 },
    });
    // Title
    slide.addText(s.title, {
      x: 0.5, y: 0.18, w: 8.5, h: 0.65,
      fontFace: FONT_HEAD, fontSize: 24, bold: true,
      color: C.titleFg, valign: 'middle', margin: 0,
    });
    // Title separator
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y: 0.88, w: 9.0, h: 0.01,
      fill: { color: C.border },
    });

    if (hasCode) {
      // Code block card
      slide.addShape(pres.shapes.RECTANGLE, {
        x: 0.5, y: 1.05, w: 9.0, h: 4.0,
        fill: { color: '010409' },
        line: { color: C.accent1, width: 1 },
        shadow: { type: 'outer', color: '00D4AA', blur: 14, offset: 0, angle: 135, opacity: 0.20 },
      });
      // Top dots (macOS style)
      const dotColors = ['FF5F57', 'FEBC2E', '28C840'];
      dotColors.forEach((col, i) => {
        slide.addShape(pres.shapes.OVAL, {
          x: 0.72 + i * 0.26, y: 1.12, w: 0.13, h: 0.13,
          fill: { color: col },
          line: { color: col, width: 0 },
        });
      });
      // Lang label
      if (s.code_lang) {
        slide.addText(s.code_lang.toUpperCase(), {
          x: 8.5, y: 1.05, w: 0.9, h: 0.3,
          fontFace: FONT_MONO, fontSize: 9, bold: true,
          color: C.accent1, align: 'right', margin: 0,
        });
      }
      slide.addText(s.code, {
        x: 0.7, y: 1.42, w: 8.6, h: 3.5,
        fontFace: FONT_MONO, fontSize: 11,
        color: C.codeText, valign: 'top', margin: 0,
      });
    } else if (hasBullets) {
      const bullets = s.bullets;
      const shown = bullets.slice(0, 6);
      const use2col = shown.length >= 3;
      const COLS = use2col ? 2 : 1;
      const cardW = COLS === 2 ? 4.3 : 9.0;
      const startX = 0.5;
      const startY = 1.1;
      const cardH = COLS === 2
        ? Math.min(1.0, 3.8 / Math.ceil(shown.length / 2))
        : Math.min(0.72, 4.2 / shown.length);
      const gapX = 0.4;
      const gapY = 0.14;

      shown.forEach((b, i) => {
        const col  = COLS === 2 ? i % 2 : 0;
        const row  = COLS === 2 ? Math.floor(i / 2) : i;
        const cx   = startX + col * (cardW + gapX);
        const cy   = startY + row * (cardH + gapY);

        // Card
        slide.addShape(pres.shapes.RECTANGLE, {
          x: cx, y: cy, w: cardW, h: cardH,
          fill: { color: C.card },
          line: { color: C.border, width: 1 },
        });
        // Accent left micro-bar
        slide.addShape(pres.shapes.RECTANGLE, {
          x: cx, y: cy, w: 0.05, h: cardH,
          fill: { color: i % 3 === 0 ? C.accent1 : i % 3 === 1 ? C.accent2 : C.accent3 },
        });
        // Text
        slide.addText(b.text, {
          x: cx + 0.18, y: cy, w: cardW - 0.26, h: cardH,
          fontFace: FONT_BODY, fontSize: 13, color: C.bodyFg,
          valign: 'middle', margin: 0,
        });
      });
    }

    // Slide counter
    slide.addText(`${(idx + 1).toString().padStart(2, '0')}`, {
      x: 9.0, y: 5.15, w: 0.7, h: 0.35,
      fontFace: FONT_MONO, fontSize: 11, bold: true,
      color: C.accent1, align: 'right', margin: 0,
    });
  }
});

pres.writeFile({ fileName: OUTPUT_PATH }).then(() => {
  console.log('OK:' + OUTPUT_PATH);
}).catch(err => {
  console.error('ERROR:' + err.message);
  process.exit(1);
});
"""


def generate_pptx(slides: list[dict], output_path: str, style: str) -> None:
    """Render slides to .pptx using pptxgenjs via Node.js."""
    template = WARM_TEMPLATE if style == "warm" else TECH_TEMPLATE

    slides_json = json.dumps(slides, ensure_ascii=False)
    abs_output  = os.path.abspath(output_path)

    js_code = (
        template
        .replace("SLIDES_JSON", slides_json)
        .replace("OUTPUT_PATH", json.dumps(abs_output))
    )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(js_code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["node", tmp_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0 or "ERROR:" in result.stdout:
            print("Node.js stderr:", result.stderr, file=sys.stderr)
            print("Node.js stdout:", result.stdout, file=sys.stderr)
            raise RuntimeError("pptxgenjs generation failed")
        print(f"✅  Saved → {abs_output}")
    finally:
        os.unlink(tmp_path)


# ─────────────────────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convert a Markdown file to a styled PowerPoint (.pptx).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Markdown structure:
          # Title           → Title slide  (# = H1)
          > subtitle text   → Subtitle / speaker note (blockquote)
          ## Section Name   → Section divider slide  (## = H2)
          ### Slide Title   → Content slide  (### = H3)
          - bullet item     → Bullet cards on content slides
          ```lang            → Code block displayed in a styled code card
          ```

        Examples:
          python md2pptx.py deck.md
          python md2pptx.py deck.md --style tech
          python md2pptx.py deck.md --style warm --output my_deck.pptx
        """),
    )
    parser.add_argument("input", help="Path to input .md file")
    parser.add_argument(
        "--style",
        choices=["warm", "tech"],
        default="warm",
        help="Visual style: 'warm' (soft & warm) or 'tech' (dark & futuristic). Default: warm",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output .pptx path. Default: <input_basename>_<style>.pptx",
    )

    args = parser.parse_args()

    # Read input
    if not os.path.isfile(args.input):
        print(f"❌  File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, encoding="utf-8") as f:
        md_text = f.read()

    # Parse
    slides = parse_markdown(md_text)
    if not slides:
        print("❌  No slides found. Make sure your Markdown has # / ## / ### headings.", file=sys.stderr)
        sys.exit(1)

    print(f"📄  Parsed {len(slides)} slides from {args.input}")

    # Output path
    if args.output:
        out_path = args.output
    else:
        base = os.path.splitext(os.path.basename(args.input))[0]
        out_path = f"{base}_{args.style}.pptx"

    # Generate
    print(f"🎨  Generating [{args.style}] style…")
    generate_pptx(slides, out_path, args.style)


if __name__ == "__main__":
    main()
