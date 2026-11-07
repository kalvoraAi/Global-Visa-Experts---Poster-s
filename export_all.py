#!/usr/bin/env python3
"""Render every poster in posters/ (and templates/) to PNG in one go.

Each HTML file declares its size with a meta tag:
    <meta name="gve-format" content="post">     (post | square | story)

Usage:
    python export_all.py              # renders posters/**/*.html -> final/
    python export_all.py templates    # renders templates/*.html  -> final/templates/
"""
import re
import sys
from pathlib import Path

from render import FORMATS, render

ROOT = Path(__file__).resolve().parent
META = re.compile(r'<meta\s+name="gve-format"\s+content="(\w+)"', re.I)


def main():
    src = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "posters")
    out_root = ROOT / "final" / (src.name if src.name != "posters" else "")
    files = sorted(src.rglob("*.html"))
    if not files:
        sys.exit(f"No .html files in {src}")

    failed = 0
    for html in files:
        m = META.search(html.read_text(encoding="utf-8"))
        fmt = m.group(1).lower() if m else "post"
        if fmt not in FORMATS:
            print(f"SKIP {html.name}: unknown format '{fmt}'")
            continue
        out = out_root / html.relative_to(src).with_suffix(".png")
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            print(render(str(html), str(out), *FORMATS[fmt]))
        except RuntimeError as e:
            failed += 1
            print(f"FAIL {html.name}: {e}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
