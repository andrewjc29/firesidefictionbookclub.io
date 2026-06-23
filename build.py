#!/usr/bin/env python3
"""
Kevin's Fireside Fiction Bookclub - site generator.

Regenerates index.html from books.json + template.html, and normalizes book covers.

How it works:
  - template.html is the full page (header, hero, Stay Connected, footer, modal,
    styles, script) with %%TOKENS%% where the per-book content goes.
  - books.json is the single source of truth for content.
  - This script fills the tokens from books.json and writes index.html.

Monthly update:
  1. Edit books.json:
       - Move the current "next" object to the TOP of "past"
         (give it a "month" label like "July 2026", drop the
         "date"/"rsvp" keys).
       - Fill "next" with the new book. Set "source_image" to the
         path of the new cover (any jpg/png/jpeg).
       - "date" holds the full line "Tuesday, August 18, 2026 . 6:30-8:00 PM".
         The part before the middle dot becomes the date line in the hero,
         the part after becomes the time line. If there is no middle dot,
         the whole string is shown as the date and the time line is omitted.
  2. Run:  python3 build.py
  3. Upload the changed index.html and the new covers/<slug>.jpg.

Covers: every book is referenced as covers/<slug>.jpg. If that file
is missing and the book has a "source_image", it is resized to 600px
wide and saved as covers/<slug>.jpg automatically.

Design changes (fonts, colors, layout) live in template.html, not here.
"""

import json, os, re, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
COVERS = os.path.join(HERE, "covers")
MAP_URL = "https://maps.app.goo.gl/Khheeku36uL8h1kXA"

# ---------- helpers ----------

def slugify(title):
    s = title.lower().replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def esc(t):
    """Escape for visible text (leaves quotes/apostrophes literal)."""
    return html.escape(t, quote=False)

def attr(t):
    """Escape for use inside a double-quoted attribute value."""
    return html.escape(t, quote=True)

def year_of(month):
    return month.strip().split()[-1]

def ensure_cover(book):
    slug = book["slug"]
    out = os.path.join(COVERS, slug + ".jpg")
    if os.path.exists(out):
        return
    src = book.get("source_image")
    if not src:
        raise SystemExit(f"MISSING COVER: covers/{slug}.jpg not found and no "
                         f"'source_image' given for \"{book['title']}\".")
    if not os.path.isabs(src):
        src = os.path.join(HERE, src)
    if not os.path.exists(src):
        raise SystemExit(f"source_image not found for \"{book['title']}\": {src}")
    from PIL import Image
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if w > 600:
        im = im.resize((600, round(h * 600 / w)), Image.LANCZOS)
    im.save(out, "JPEG", quality=82, optimize=True)
    print(f"  normalized cover -> covers/{slug}.jpg ({im.size[0]}x{im.size[1]})")

# ---------- block builders ----------

CLOCK_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
             'aria-hidden="true"><circle cx="12" cy="12" r="9"></circle>'
             '<path d="M12 7v5l3 2"></path></svg>')

def time_row(time_text):
    if not time_text:
        return ""
    return (
        '            <p class="info-row">\n'
        f'              {CLOCK_SVG}\n'
        f'              <span class="date-strong">{esc(time_text)}</span>\n'
        '            </p>\n'
    )

def grid_button(b):
    t, a, g, m = b["title"], b["author"], b["genre"], b["month"]
    return (
        '        <button class="grid-book" type="button"\n'
        f'          data-title="{attr(t)}" data-author="{attr(a)}" '
        f'data-genre="{attr(g)}" data-month="{attr(m)}"\n'
        f'          data-desc="{attr(b["desc"])}">\n'
        f'          <span class="grid-cover-wrap"><img class="cover" '
        f'src="covers/{b["slug"]}.jpg" loading="lazy" '
        f'alt="Cover of {attr(t)} by {attr(a)}"></span>\n'
        f'          <span class="grid-meta"><span class="grid-title">{esc(t)}</span>'
        f'<span class="grid-author">{esc(a)}</span></span>\n'
        '        </button>'
    )

def past_groups(past):
    # Group by year, preserving the newest-first order of books.json.
    order = []
    groups = {}
    for b in past:
        y = year_of(b["month"])
        if y not in groups:
            groups[y] = []
            order.append(y)
        groups[y].append(b)
    chunks = []
    for y in order:
        buttons = "\n".join(grid_button(b) for b in groups[y])
        chunks.append(
            f'      <h3 class="year">{esc(y)}</h3>\n'
            f'      <div class="cover-grid">\n{buttons}\n      </div>'
        )
    return "\n\n".join(chunks)

def split_date(raw):
    # "Tuesday, July 21, 2026 . 6:30-8:00 PM" -> (date, time) on the middle dot.
    if "·" in raw:
        d, t = raw.split("·", 1)
        return d.strip(), t.strip()
    return raw.strip(), ""

# ---------- render ----------

def render(data, template):
    nxt = data["next"]
    nxt["slug"] = slugify(nxt["title"])
    ensure_cover(nxt)
    for b in data["past"]:
        b["slug"] = slugify(b["title"])
        ensure_cover(b)

    date_text, time_text = split_date(nxt["date"])
    out = template
    repl = {
        "%%NEXT_SLUG%%": nxt["slug"],
        "%%TITLE%%": esc(nxt["title"]),
        "%%AUTHOR%%": esc(nxt["author"]),
        "%%GENRE%%": esc(nxt["genre"]),
        "%%DATE%%": esc(date_text),
        "%%RSVP%%": attr(nxt["rsvp"]),
        "%%DESC%%": esc(nxt["desc"]),
        "%%PAST_GROUPS%%": past_groups(data["past"]),
    }
    # Time row first (it contains other tokens-free markup), then the rest.
    out = out.replace("%%TIME_ROW%%", time_row(time_text))
    for k, v in repl.items():
        out = out.replace(k, v)
    return out

# ---------- main ----------

def main():
    with open(os.path.join(HERE, "books.json"), encoding="utf-8") as f:
        data = json.load(f)
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        template = f.read()
    out = render(data, template)
    if "%%" in out:
        leftover = sorted(set(re.findall(r"%%[A-Z_]+%%", out)))
        raise SystemExit(f"Unfilled tokens remain: {leftover}")
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote index.html  (1 next read + {len(data['past'])} past reads)")

if __name__ == "__main__":
    main()
