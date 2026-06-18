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

# ---------- block templates ----------

def next_block(b):
    return f"""    <p class="date">{esc(b['date'])}</p>
    <a class="rsvp" href="{esc(b['rsvp'])}">RSVP on Luma &rarr;</a>
    <div class="next-grid">
      <div class="next-cover">
        <img class="cover" src="covers/{b['slug']}.jpg"
             alt="Cover of {esc(b['title'])} by {esc(b['author'])}" fetchpriority="high">
      </div>
      <div class="next-body">
        <h3 id="next-title">{esc(b['title'])}</h3>
        <p class="author">by {esc(b['author'])}</p>
        <span class="genre">{esc(b['genre'])}</span>
        <details class="more">
          <summary>Read more</summary>
          <p class="desc">{esc(b['desc'])}</p>
        </details>
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
        <details class="more">
          <summary>Read more</summary>
          <p class="desc">{esc(b['desc'])}</p>
        </details>
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
<meta name="theme-color" content="#23459e">
<meta property="og:title" content="Kevin's Fireside Fiction Bookclub">
<meta property="og:description" content="No genre is off limits. If it's fiction, it's fair game. All readers welcome.">
<meta property="og:type" content="website">
<title>Kevin's Fireside Fiction Bookclub</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,900;1,9..144,400;1,9..144,600&family=Spectral:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<style>
  :root{{
    --ink:#1b2a52;
    --blue:#23459e;
    --blue-bright:#2f57c9;
    --blue-deep:#15264f;
    --cream:#f4ead2;
    --paper:#fcf6e6;
    --tan:#e0cfa6;
    --rust:#9d4426;
    --muted:#5a678f;
    --maxw:780px;
  }}
  *{{box-sizing:border-box;}}
  html{{-webkit-text-size-adjust:100%;scroll-behavior:smooth;}}
  body{{
    margin:0;
    border-top:6px solid var(--blue);
    color:var(--ink);
    background-color:var(--cream);
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E");
    font-family:'Spectral',Georgia,'Times New Roman',serif;
    font-size:18px;
    line-height:1.65;
  }}
  .wrap{{max-width:var(--maxw);margin:0 auto;padding:0 22px;}}
  a{{color:var(--blue);}}
  a:hover,a:focus{{color:var(--blue-bright);}}

  /* ---------- Header ---------- */
  header.site{{
    text-align:center;
    padding:50px 22px 0;
  }}
  header.site h1.brand{{margin:0;line-height:0;}}
  header.site h1.brand img{{
    display:block;
    width:100%;
    max-width:430px;
    height:auto;
    margin:0 auto;
  }}
  .tagline{{
    font-family:'Fraunces',Georgia,serif;
    font-style:italic;
    font-weight:400;
    font-size:clamp(1.1rem,3.6vw,1.4rem);
    color:var(--blue);
    max-width:30ch;
    margin:18px auto 0;
    line-height:1.4;
  }}
  .meet{{
    margin:24px auto 0;
    display:flex;
    flex-direction:column;
    gap:9px;
    align-items:center;
    font-size:0.98rem;
    color:var(--ink);
  }}
  .meet-item{{display:flex;gap:9px;align-items:center;margin:0;text-align:left;}}
  .meet-item svg{{width:19px;height:19px;color:var(--blue);flex:0 0 auto;}}

  .divider{{
    width:100%;max-width:var(--maxw);
    margin:34px auto 0;
    display:flex;align-items:center;justify-content:center;gap:14px;
    color:var(--tan);
  }}
  .divider::before,.divider::after{{
    content:"";height:1px;flex:1;background:var(--tan);
  }}
  .divider span{{color:var(--blue);font-size:1rem;letter-spacing:3px;}}

  /* ---------- Section titles ---------- */
  .section-title{{
    font-family:'Fraunces',Georgia,serif;
    font-weight:600;
    font-size:clamp(1.7rem,5.5vw,2.4rem);
    color:var(--ink);
    margin:46px 0 0;
    letter-spacing:-0.01em;
  }}
  .section-title::after{{
    content:"";
    display:block;
    width:56px;height:4px;
    background:var(--blue);
    border-radius:2px;
    margin-top:10px;
  }}

  /* ---------- Next Read (featured) ---------- */
  .next{{
    position:relative;
    background:var(--paper);
    border:1px solid var(--tan);
    border-radius:14px;
    padding:28px;
    margin-top:20px;
    box-shadow:0 14px 34px rgba(21,38,79,0.10);
  }}
  .next::before{{
    content:"";
    position:absolute;left:0;top:0;height:100%;width:6px;
    background:var(--blue);
    border-radius:14px 0 0 14px;
  }}
  .next .date{{
    font-family:'Fraunces',Georgia,serif;
    font-weight:700;
    color:var(--rust);
    font-size:clamp(1.3rem,5vw,1.9rem);
    line-height:1.15;
    margin:0 0 14px;
  }}
  .next-grid{{display:flex;gap:26px;flex-wrap:wrap;align-items:flex-start;justify-content:center;}}
  .next-cover{{flex:0 0 185px;}}
  .next-body{{flex:1 1 270px;min-width:240px;}}
  .next-body h3{{
    font-family:'Fraunces',Georgia,serif;
    font-weight:900;
    font-size:clamp(1.9rem,6vw,2.7rem);
    line-height:1.02;
    margin:0 0 6px;
    color:var(--ink);
  }}
  .author{{
    font-family:'Fraunces',Georgia,serif;
    font-style:italic;
    font-weight:400;
    color:var(--muted);
    margin:0 0 10px;
    font-size:1.12rem;
  }}
  .genre{{
    display:inline-block;
    font-family:'Spectral',serif;
    text-transform:uppercase;
    letter-spacing:1.6px;
    font-size:0.68rem;
    font-weight:600;
    color:var(--blue);
    background:rgba(35,69,158,0.07);
    border:1px solid var(--blue);
    padding:4px 12px;
    border-radius:999px;
    margin-bottom:12px;
  }}
  .desc{{margin:10px 0 0;font-size:1rem;line-height:1.7;}}

  /* Covers: uniform 2:3 portrait, framed like a real book */
  .cover{{
    display:block;
    width:100%;
    aspect-ratio:2/3;
    object-fit:cover;
    border-radius:3px;
    background:var(--tan);
    box-shadow:0 1px 2px rgba(0,0,0,0.22), 0 10px 24px rgba(21,38,79,0.20);
    transition:transform .18s ease, box-shadow .18s ease;
  }}

  .rsvp{{
    display:inline-block;
    margin:2px 0 22px;
    background:var(--rust);
    color:#fff;
    font-family:'Fraunces',Georgia,serif;
    font-weight:600;
    letter-spacing:0.3px;
    font-size:1.05rem;
    text-decoration:none;
    padding:13px 30px;
    border-radius:9px;
    box-shadow:0 5px 16px rgba(157,68,38,0.30);
    transition:transform .15s ease, background .15s ease;
  }}
  .rsvp:hover,.rsvp:focus{{background:#85391f;color:#fff;transform:translateY(-1px);}}

  /* ---------- Read more toggles ---------- */
  details.more{{margin-top:10px;}}
  details.more > summary{{
    cursor:pointer;
    width:max-content;
    font-family:'Fraunces',Georgia,serif;
    font-weight:600;
    font-size:0.92rem;
    color:var(--blue);
  }}
  details.more > summary:hover,details.more > summary:focus{{color:var(--blue-bright);}}
  details.more[open] > summary{{margin-bottom:6px;}}
  details.more .desc{{margin-top:0;}}

  /* ---------- Past Reads ---------- */
  .past-list{{margin-top:22px;}}
  .book{{
    display:flex;
    gap:22px;
    padding:24px 0;
    border-bottom:1px solid var(--tan);
  }}
  .book:hover .cover{{transform:translateY(-4px);box-shadow:0 2px 4px rgba(0,0,0,0.22), 0 16px 30px rgba(21,38,79,0.26);}}
  .book-cover{{flex:0 0 100px;}}
  .book-body{{flex:1;min-width:0;}}
  .book .month{{
    font-family:'Spectral',serif;
    text-transform:uppercase;
    letter-spacing:2px;
    font-size:0.7rem;
    font-weight:600;
    color:var(--rust);
    margin:0 0 4px;
  }}
  .book-body h3{{
    font-family:'Fraunces',Georgia,serif;
    font-weight:600;
    font-size:1.5rem;
    line-height:1.08;
    margin:0 0 3px;
    color:var(--ink);
  }}
  .book-body .author{{font-size:0.98rem;margin-bottom:8px;}}
  .book-body .genre{{font-size:0.62rem;padding:3px 10px;margin-bottom:9px;}}
  .book-body .desc{{font-size:0.93rem;line-height:1.65;color:#33406b;}}

  /* ---------- Footer ---------- */
  footer.site{{
    margin-top:58px;
    background:var(--blue-deep);
    color:var(--cream);
    padding:40px 22px 56px;
    text-align:center;
  }}
  .footer-inner{{max-width:var(--maxw);margin:0 auto;}}
  .links{{
    display:flex;
    flex-wrap:wrap;
    justify-content:center;
    gap:12px;
    margin-bottom:24px;
  }}
  .links a{{
    font-family:'Fraunces',Georgia,serif;
    font-weight:600;
    font-size:1rem;
    text-decoration:none;
    color:var(--cream);
    background:rgba(255,255,255,0.08);
    border:1px solid rgba(244,234,210,0.30);
    padding:10px 22px;
    border-radius:9px;
    transition:background .15s ease, color .15s ease;
  }}
  .links a:hover,.links a:focus{{background:var(--cream);color:var(--blue-deep);}}
  .footer-note{{
    font-family:'Spectral',serif;
    font-size:0.9rem;
    color:rgba(244,234,210,0.78);
    line-height:1.8;
  }}
  .footer-note strong{{
    font-family:'Fraunces',Georgia,serif;
    font-weight:600;
    color:var(--cream);
    font-size:1.02rem;
  }}

  @media (max-width:480px){{
    body{{font-size:17px;}}
    .next{{padding:22px;}}
    .next-cover{{flex-basis:165px;}}
    .book-cover{{flex-basis:84px;}}
    .book{{gap:16px;}}
  }}
</style>
</head>
<body>

<header class="site">
  <div class="wrap">
    <h1 class="brand"><img src="logo.png" alt="Kevin's Fireside Fiction Bookclub"></h1>
    <p class="tagline">No genre is off limits. If it's fiction, it's fair game. All readers welcome.</p>
    <div class="meet">
      <p class="meet-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path></svg>
        3rd Tuesday of every month, 6:30&ndash;8:00&nbsp;PM
      </p>
      <p class="meet-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-5.2-7-11a7 7 0 0 1 14 0c0 5.8-7 11-7 11z"></path><circle cx="12" cy="10" r="2.6"></circle></svg>
        <span><a href="https://maps.app.goo.gl/Khheeku36uL8h1kXA">Fireside Books &amp; More</a>, 2421 Broadway, Redwood City, CA</span>
      </p>
    </div>
  </div>
  <div class="divider"><span>&#10070;</span></div>
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
  <div class="footer-inner">
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
