# Kevin's Fireside Fiction Bookclub — Reading List Site

A single static page (`index.html`) that replaces the Google Doc reading list. No build step, no JavaScript framework, no dependencies except a Google Font. Hosts free on GitHub Pages.

## Files

```
index.html        The whole site (HTML + inline CSS) — this is what GitHub Pages serves
covers/           Portrait book covers, named by slug: covers/[book-slug].jpg
books.json        All book data (the single source of truth for content)
build.py          Regenerates index.html from books.json and normalizes covers
README.md         This file
```

`index.html` is generated from `books.json` by `build.py`. You can either edit
`books.json` and re-run the script (recommended, see "Monthly update"), or hand-edit
`index.html` directly. Either works; the script just removes the chance of breaking
the HTML by hand.

## Deploy on GitHub Pages

1. Put `index.html` and the `covers/` folder in the root of your repo (`andrewjc29/firesidefictionbookclub.io`). Commit and push to the `main` branch.
2. On GitHub, open the repo, go to **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **Deploy from a branch**.
4. Set **Branch** to `main` and folder to `/ (root)`. Click **Save**.
5. Wait about a minute. GitHub shows the live URL at the top of the Pages settings. It will be:

   ```
   https://andrewjc29.github.io/firesidefictionbookclub.io/
   ```

6. Open it on your phone to confirm covers and links load. Then re-point your bit.ly to that URL.

## Monthly update (recommended: edit `books.json`, run `build.py`)

You only edit `books.json`. It has one `next` object and a `past` array (newest first).

### 1. In `books.json`, move the old Next Read into Past Reads

Take the current `next` object, move it to the **top** of the `past` array. Replace its
`date` and `rsvp` keys with a single `month` key (e.g. `"month": "July 2026"`). Remove
`source_image` if present.

### 2. Fill in the new `next`

```json
"next": {
  "title": "The New Book",
  "author": "Author Name",
  "genre": "Literary Fiction",
  "date": "Tuesday, August 18, 2026 · 6:30–8:00 PM",
  "rsvp": "https://luma.com/xxxxxxxx",
  "desc": "Two to three sentence description.",
  "source_image": "/path/to/the-new-cover.jpg"
}
```

`source_image` is the new cover anywhere on disk (jpg/png/jpeg). The script resizes it
to 600px wide and saves it as `covers/<slug>.jpg` for you. The slug is derived from the
title automatically (e.g. "The New Book" becomes `the-new-book`). Once the cover exists in
`covers/`, you can drop `source_image`.

### 3. Run the generator

```
python3 build.py
```

This rewrites `index.html` and creates any missing cover. It prints a clear error if a
cover is missing and no `source_image` was given, so nothing publishes half-broken.

### 4. Commit and push

```
git add .
git commit -m "Update: [new book title] for [month]"
git push
```

GitHub Pages redeploys in about a minute. The bit.ly and Linktree links never change.

> One-time setup for the script: `pip install Pillow` (only needed for cover resizing).

### Alternative: hand-edit `index.html`

If you'd rather not run the script, edit `index.html` directly. Copy the current Next Read
`<section class="next">` content into a new `<article class="book">` at the top of
`.past-list`, then update the Next Read fields. Add the new cover to `covers/` as
`covers/<slug>.jpg` yourself.

## Standard links (in the footer)

- Luma calendar: https://luma.com/kevinsbookclub
- Discord: https://discord.gg/KWzm3Kh9Sh
- Linktree: https://linktr.ee/kevinsbookclub

## Notes

- The page uses one web font (Bebas Neue) loaded from Google Fonts. If a reader is offline it falls back to a system condensed font; everything still works.
- Covers are referenced by relative path, so the site is fully self-contained and portable.
- Meeting details (3rd Tuesday, 6:30–8:00 PM, Fireside Books & More, 2421 Broadway, Redwood City, CA 94063) live in the header and footer of `index.html` if you ever need to change them.
