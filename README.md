# GVE Posters

Instagram posters and stories for **Global Visa Experts**, built as HTML/CSS
and exported to exact-size PNGs.

## Folders

| Folder | What goes there |
|---|---|
| `brand/` | Brand kit: `BRAND.md`, `brand.css`, `logo/`, `fonts/` |
| `templates/` | Starter designs: post 4:5, square 1:1, story 9:16 |
| `posters/` | Real client posters (copy a template here, e.g. `posters/2026-11/canada-intake.html`) |
| `assets/` | Photos and images used in posters (only ones you have rights to) |
| `drafts/` | Work in progress, Canva/PSD files, rough ideas |
| `references/` | Mood board screenshots — for style only, never copy them |
| `final/` | Exported PNGs ready to post (generated) |

## Sizes

| Format | Size | Meta tag |
|---|---|---|
| Post (portrait) | 1080×1350 | `<meta name="gve-format" content="post">` |
| Square | 1080×1080 | `<meta name="gve-format" content="square">` |
| Story | 1080×1920 | `<meta name="gve-format" content="story">` — keep text out of top 250px and bottom 340px |

## Setup (once)

```bash
pip install playwright pillow
python -m playwright install chromium
```

(If Playwright isn't installed, the scripts fall back to Chrome or Edge.)

## Make a poster

1. Copy a template from `templates/` into `posters/`.
2. Edit the text, colour scheme class (`royal`, `crimson`, `teal`, `white`) and image.
3. Export:

```bash
python render.py posters/canada-intake.html final/canada-intake.png --format post
```

## Export everything

```bash
python export_all.py            # all posters/ -> final/
python export_all.py templates  # preview the templates -> final/templates/
```
