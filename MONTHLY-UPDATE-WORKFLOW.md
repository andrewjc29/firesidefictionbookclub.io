# Reading List Site: Monthly Update

- Live site: https://andrewjc29.github.io/firesidefictionbookclub.io/
- Repo: https://github.com/andrewjc29/firesidefictionbookclub.io
- bit.ly and Linktree point here. Never change those.

You edit one file (`books.json`), run one script (`build.py`), publish the changed files (`index.html` and the new cover). The page design lives in `template.html` and only changes when you redesign the site, not monthly.

## Where the files live

The GitHub repo is the source of truth. `build.py`, `books.json`, `template.html`, and `covers/` sit together in the repo root, and `build.py` finds them automatically because it looks in its own folder. The only path you supply is the new cover's `source_image`. `index.html` is generated, so never hand-edit it; edit `books.json` (content) or `template.html` (design) and rebuild.

Before editing, pull the current files from the repo so you never work from a stale copy. Edit in one place only.

## Steps

1. Edit `books.json`. Move the current `next` to the top of `past`: replace its `date` and `rsvp` keys with one `month` key (e.g. `"month": "July 2026"`), remove `source_image`. Then fill `next` with the new book:

   ```json
   "next": {
     "title": "The New Book",
     "author": "Author Name",
     "genre": "Literary Fiction",
     "date": "Tuesday, August 18, 2026 · 6:30–8:00 PM",
     "rsvp": "https://luma.com/xxxxxxxx",
     "desc": "Two to three sentence description.",
     "source_image": "/full/path/to/new-cover.jpg"
   }
   ```

   Keep the middle dot (`·`) in `date` between the date and the time: the hero splits on it to show a date line and a time line. Write `desc` as a full two-to-four sentence blurb. It shows in the hero "View details" toggle this month and in the Past Reads pop-up after the book rolls into `past`.

   `source_image` is the cover anywhere on your Mac. The script resizes it and saves `covers/<slug>.jpg`. First run only: `pip install Pillow`.

2. Run it:

   ```
   python3 build.py
   ```

3. Publish. In the repo: Add file, Upload files, drag in `index.html` and the new `covers/<slug>.jpg`, commit. Live in ~1 minute.

## Verify

Open the live site on your phone. New book under Next Read with cover, RSVP button works, last month moved to top of Past Reads. Hard refresh if you see the old version.

## Where it goes in the monthly update

Run after the Luma event exists (for the RSVP link) and the cover is exported. It does not depend on Discord, Linktree, or Canva, so position is flexible after that.

## Letting Claude do it

Give Claude the new book details and the cover. Claude edits `books.json`, runs `build.py`, and publishes the two files through Chrome with your OK before commit. Stay signed into GitHub in Chrome.
