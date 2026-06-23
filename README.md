# Kevin's Fireside Fiction Bookclub — Reading List Site

A single static page (`index.html`) that replaces the Google Doc reading list. No build step, no JavaScript framework, no dependencies except a Google Font. Hosts free on GitHub Pages.

## Files

```
index.html        Generated output. This is what GitHub Pages serves. Do not hand-edit.
template.html     The page design (layout, inline CSS, fonts, JS) with %%TOKENS%% for content
books.json        All book data (the single source of truth for content)
build.py          Fills template.html from books.json into index.html, and normalizes covers
covers/           Portrait book covers, named by slug: covers/[book-slug].jpg
logo.png          The title logo image. Do not modify, recreate, or recolor it.
README.md         This file
```

`index.html` is generated from `books.json` and `template.html` by `build.py`.
Edit `books.json` and re-run the script (see "Monthly update"). Do not hand-edit
`index.html`: it is overwritten on every build. To change the design (layout,
colors, fonts, the Stay Connected or footer sections), edit `template.html`.

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
  "desc": "Two to four sentence description.",
  "source_image": "/path/to/the-new-cover.jpg"
}
```

The `date` field is split on the middle dot (`·`): the part before it becomes the
date line in the hero, the part after becomes the time line. Keep that dot between
the date and the time. The hero shows `genre` and `desc` inside the "View details"
toggle; the same `desc` appears in the Past Reads pop-up after the book rolls into
`past`, so write it as a full two-to-four sentence blurb.

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

### Do not hand-edit `index.html`

`index.html` is regenerated on every build, so any direct edits are lost. Change content
in `books.json` and design in `template.html`, then run `build.py`.

## Standard links (in the Stay Connected section)

- Discord: https://discord.gg/KWzm3Kh9Sh
- Luma calendar: https://luma.com/kevinsbookclub
- Linktree: https://linktr.ee/kevinsbookclub

These three live in the Stay Connected section near the bottom of `template.html`.

## Notes

- The page uses two web fonts from Google Fonts: Bitter for headings, Spectral for body. Offline, both fall back to Georgia/serif and everything still works.
- Covers are referenced by relative path, so the site is fully self-contained and portable.
- Meeting date and time come from `books.json` (`next.date`). The location link, the meeting schedule, and the footer text live in `template.html`.
- The Past Reads pop-up and the hero "View details" toggle are powered by a small inline script at the bottom of `template.html`. No framework, no dependencies.
