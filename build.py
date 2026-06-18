#!/usr/bin/env python3
"""
Kevin's Fireside Fiction Bookclub - site generator.

Regenerates index.html from books.json and normalizes book covers.

Monthly update:
  1. Edit books.json:
       - Move the current "next" object to the TOP of "past"
         (give it a "month" label like "July 2026", drop the
         "date"/"rsvp" keys).
       - Fill "next" with the new book. Set "source_image" to the
         path of the new cover (any jpg/png/jpeg).
  2. Run:  python3 build.py
  3. Upload the changed index.html and the new covers/<slug>.jpg.

Covers: every book is referenced as covers/<slug>.jpg. If that file
is missing and the book has a "source_image", it is resized to 600px
wide and saved as covers/<slug>.jpg automatically.
"""

import json, os, re, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
COVERS = os.path.join(HERE, "covers")

# ---------- helpers ----------

def slugify(title):
    s = title.lower().replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def esc(t):
    # escape HTML, then restore the typographic dashes we want to keep
    return html.escape(t, quote=False)

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

# ---------- templates ----------

def next_block(b):
    return f"""    <p class="date">{esc(b['date'])}</p>
    <div class="next-grid">
      <div class="next-cover">
        <img class="cover" src="covers/{b['slug']}.jpg"
             alt="Cover of {esc(b['title'])} by {esc(b['author'])}" fetchpriority="high">
      </div>
      <div class="next-body">
        <h3 id="next-title">{esc(b['title'])}</h3>
        <p class="author">by {esc(b['author'])}</p>
        <span class="genre">{esc(b['genre'])}</span>
        <p class="desc">{esc(b['desc'])}</p>
        <a class="rsvp" href="{esc(b['rsvp'])}">RSVP on Luma</a>
      </div>
    </div>"""

def past_block(b):
    return f"""    <article class="book">
      <div class="book-cover">
        <img class="cover" src="covers/{b['slug']}.jpg" loading="lazy"
             alt="Cover of {esc(b['title'])} by {esc(b['author'])}">
      </div>
      <div class="book-body">
        <p class="month">{esc(b['month'])}</p>
        <h3>{esc(b['title'])}</h3>
        <p class="author">by {esc(b['author'])}</p>
        <span class="genre">{esc(b['genre'])}</span>
        <p class="desc">{esc(b['desc'])}</p>
      </div>
    </article>"""

def render(data):
    nxt = data["next"]
    nxt["slug"] = slugify(nxt["title"])
    ensure_cover(nxt)
    past_html = []
    for b in data["past"]:
        b["slug"] = slugify(b["title"])
        ensure_cover(b)
        past_html.append(past_block(b))
    return PAGE.format(next_block=next_block(nxt),
                       past_blocks="\n\n".join(past_html),
                       next_rsvp=esc(nxt["rsvp"]))

# ---------- main ----------

def main():
    with open(os.path.join(HERE, "books.json"), encoding="utf-8") as f:
        data = json.load(f)
    out = render(data)
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote index.html  (1 next read + {len(data['past'])} past reads)")

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Kevin's Fireside Fiction Bookclub reading list. We meet the 3rd Tuesday of every month at Fireside Books & More in Redwood City, CA. All readers welcome.">
<meta name="theme-color" content="#1d2a4f">
<meta property="og:title" content="Kevin's Fireside Fiction Bookclub">
<meta property="og:description" content="No genre is off limits. If it's fiction, it's fair game. All readers welcome.">
<meta property="og:type" content="website">
<title>Kevin's Fireside Fiction Bookclub</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet">
<style>
  :root{{
    --navy:#1d2a4f;
    --navy-soft:#3a4a73;
    --cream:#f7efdd;
    --cream-card:#fcf7ea;
    --line:#e2d6b8;
    --accent:#9c3b2e;
    --maxw:760px;
  }}
  *{{box-sizing:border-box;}}
  html{{-webkit-text-size-adjust:100%;}}
  body{{
    margin:0;
    background:var(--cream);
    color:var(--navy);
    font-family:Georgia,'Times New Roman',serif;
    font-size:17px;
    line-height:1.6;
  }}
  .wrap{{max-width:var(--maxw);margin:0 auto;padding:0 20px;}}
  a{{color:var(--accent);}}
  a:hover,a:focus{{text-decoration:underline;}}

  header.site{{
    text-align:center;
    padding:42px 20px 30px;
    border-bottom:3px double var(--navy);
  }}
  header.site h1{{
    font-family:'Bebas Neue',Impact,sans-serif;
    font-weight:400;
    margin:0;
    line-height:0.95;
    letter-spacing:1.5px;
    font-size:clamp(2.6rem,9vw,4.4rem);
  }}
  header.site h1.brand{{margin:0;line-height:0;}}
  header.site h1.brand img{{
    display:block;
    width:100%;
    max-width:420px;
    height:auto;
    margin:0 auto;
  }}
  .tagline{{
    font-style:italic;
    margin:14px auto 0;
    max-width:32em;
    color:var(--navy-soft);
  }}
  .meet{{
    margin-top:18px;
    font-size:0.95rem;
    line-height:1.7;
  }}
  .meet strong{{
    font-family:'Bebas Neue',Impact,sans-serif;
    letter-spacing:1px;
    font-weight:400;
    font-size:1.05rem;
  }}

  .section-title{{
    font-family:'Bebas Neue',Impact,sans-serif;
    font-weight:400;
    letter-spacing:2px;
    font-size:1.9rem;
    margin:44px 0 4px;
    padding-bottom:6px;
    border-bottom:2px solid var(--navy);
  }}

  .next{{
    background:var(--cream-card);
    border:1px solid var(--line);
    border-top:6px solid var(--navy);
    border-radius:10px;
    padding:22px;
    margin-top:16px;
    box-shadow:0 2px 10px rgba(29,42,79,0.06);
  }}
  .next .date{{
    font-family:'Bebas Neue',Impact,sans-serif;
    letter-spacing:1.5px;
    font-size:1.25rem;
    margin:0 0 14px;
  }}
  .next-grid{{display:flex;gap:22px;flex-wrap:wrap;align-items:flex-start;justify-content:center;}}
  .next-cover{{flex:0 0 175px;}}
  .next-body{{flex:1 1 260px;min-width:230px;}}
  .next-body h3{{
    font-family:'Bebas Neue',Impact,sans-serif;
    font-weight:400;
    letter-spacing:1px;
    font-size:2rem;
    line-height:1;
    margin:0 0 4px;
  }}
  .author{{font-style:italic;margin:0 0 6px;color:var(--navy-soft);}}
  .genre{{
    display:inline-block;
    font-family:'Bebas Neue',Impact,sans-serif;
    letter-spacing:1.5px;
    font-size:0.85rem;
    background:var(--navy);
    color:var(--cream);
    padding:3px 10px;
    border-radius:3px;
    margin-bottom:10px;
  }}
  .desc{{margin:8px 0 0;font-size:0.98rem;}}

  .cover{{
    display:block;
    width:100%;
    aspect-ratio:2/3;
    object-fit:cover;
    border-radius:6px;
    background:var(--line);
    box-shadow:0 3px 8px rgba(29,42,79,0.18);
  }}

  .rsvp{{
    display:inline-block;
    margin-top:16px;
    background:var(--accent);
    color:#fff;
    font-family:'Bebas Neue',Impact,sans-serif;
    letter-spacing:1.5px;
    font-size:1.25rem;
    text-decoration:none;
    padding:11px 30px;
    border-radius:6px;
  }}
  .rsvp:hover,.rsvp:focus{{background:#822f25;text-decoration:none;}}

  .past-list{{margin-top:18px;}}
  .book{{
    display:flex;
    gap:18px;
    padding:18px 0;
    border-bottom:1px solid var(--line);
  }}
  .book .month{{
    font-family:'Bebas Neue',Impact,sans-serif;
    letter-spacing:1px;
    font-size:0.8rem;
    color:var(--navy-soft);
    margin:0 0 3px;
  }}
  .book-cover{{flex:0 0 92px;}}
  .book-body{{flex:1;min-width:0;}}
  .book-body h3{{
    font-family:'Bebas Neue',Impact,sans-serif;
    font-weight:400;
    letter-spacing:0.5px;
    font-size:1.4rem;
    line-height:1.05;
    margin:0 0 2px;
  }}
  .book-body .author{{font-size:0.92rem;margin-bottom:6px;}}
  .book-body .genre{{font-size:0.72rem;padding:2px 8px;margin-bottom:8px;}}
  .book-body .desc{{font-size:0.92rem;}}

  footer.site{{
    margin-top:46px;
    padding:30px 20px 50px;
    border-top:3px double var(--navy);
    text-align:center;
  }}
  .links{{
    display:flex;
    flex-wrap:wrap;
    justify-content:center;
    gap:12px;
    margin-bottom:20px;
  }}
  .links a{{
    font-family:'Bebas Neue',Impact,sans-serif;
    letter-spacing:1.5px;
    font-size:1.1rem;
    text-decoration:none;
    color:var(--cream);
    background:var(--navy);
    padding:9px 22px;
    border-radius:6px;
  }}
  .links a:hover,.links a:focus{{background:var(--navy-soft);text-decoration:none;}}
  .footer-note{{
    font-size:0.85rem;
    color:var(--navy-soft);
    line-height:1.7;
  }}
  .footer-note strong{{
    font-family:'Bebas Neue',Impact,sans-serif;
    letter-spacing:1px;
    font-weight:400;
  }}

  @media (max-width:480px){{
    .next-cover{{flex-basis:160px;}}
    .book-cover{{flex-basis:80px;}}
  }}
</style>
</head>
<body>

<header class="site">
  <div class="wrap">
    <h1 class="brand"><img src="logo.png" alt="Kevin's Fireside Fiction Bookclub"></h1>
    <p class="tagline">No genre is off limits. If it's fiction, it's fair game. All readers welcome.</p>
    <p class="meet">
      <strong>When:</strong> 3rd Tuesday of every month, 6:30&ndash;8:00&nbsp;PM<br>
      <strong>Where:</strong> <a href="https://maps.app.goo.gl/Khheeku36uL8h1kXA">Fireside Books &amp; More</a>, 2421 Broadway, Redwood City, CA&nbsp;94063
    </p>
  </div>
</header>

<main class="wrap">

  <!-- NEXT READ  (generated from books.json -> "next") -->
  <h2 class="section-title">Next Read</h2>
  <section class="next" aria-labelledby="next-title">
{next_block}
  </section>

  <!-- PAST READS  (generated from books.json -> "past", newest first) -->
  <h2 class="section-title">Past Reads</h2>
  <div class="past-list">

{past_blocks}

  </div>

</main>

<footer class="site">
  <div class="wrap">
    <nav class="links" aria-label="Bookclub links">
      <a href="{next_rsvp}">RSVP Next Read</a>
      <a href="https://luma.com/kevinsbookclub">Luma Calendar</a>
      <a href="https://discord.gg/KWzm3Kh9Sh">Discord</a>
      <a href="https://linktr.ee/kevinsbookclub">Linktree</a>
    </nav>
    <p class="footer-note">
      <strong>Kevin's Fireside Fiction Bookclub</strong><br>
      3rd Tuesday Monthly &middot; 6:30&nbsp;PM &middot; Fireside Books &amp; More
    </p>
  </div>
</footer>

</body>
</html>
"""

if __name__ == "__main__":
    main()
