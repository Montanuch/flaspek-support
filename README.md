# flaspek-support

Public site for the Flaspek iOS app: support & FAQ, Privacy Policy, Terms of Use.
Served by GitHub Pages at <https://montanuch.github.io/flaspek-support/>. The app
(`Services/SupportLinks.swift`) and App Store Connect link to the three root URLs —
do not move `index.html`, `privacy.html`, `terms.html`.

## Layout

| Path | What |
|---|---|
| `index.html` | English support page — **generated**, do not edit by hand |
| `<code>/index.html` | the same page in another language (`ru/`, `es/`, `zh/`, …) — generated |
| `privacy.html`, `terms.html` | legal pages, hand-written, EN + RU in one document with a JS switch |
| `tools/template.html` | the page template (`{{placeholders}}`) |
| `tools/content/<code>.json` | all text of one locale; same keys everywhere, `en.json` is the reference |
| `tools/build.py` | renders template × content → pages, `sitemap.xml`, the page list in `llms.txt` |
| `og-image.png` | 1200×630 share image, rendered from the app icon |
| `llms.txt`, `robots.txt`, `.nojekyll` | AEO summary for AI crawlers, crawler policy, raw-static flag |

## Editing

1. Change text in `tools/content/<code>.json` (or `template.html` for structure/CSS).
   Keep UI labels identical to the app's `Localizable.xcstrings` for that locale.
2. `python3 tools/build.py` — rebuilds every page whose JSON exists, validates that
   each locale has the English keys and 14 FAQ entries.
3. Commit the generated files together with the sources; GitHub Pages serves the result.

Adding a locale: add a row to `LOCALES` in `build.py`, create `tools/content/<code>.json`
with every key of `en.json`, run the build.
