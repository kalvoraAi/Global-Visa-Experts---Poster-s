#!/usr/bin/env python3
"""Render an HTML design to a PNG at an exact Instagram size.

Usage:
    python render.py design.html output.png --format post|square|story
    python render.py design.html output.png --width 1080 --height 1350

Tries Playwright first, then headless Chrome/Chromium/Edge directly. Prints the
final pixel size so you can confirm it matches the format.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FORMATS = {
    "post": (1080, 1350),    # 4:5 portrait feed post (default)
    "square": (1080, 1080),  # 1:1 feed post
    "story": (1080, 1920),   # 9:16 story / reel cover
}

CHROME_CANDIDATES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_chrome():
    for c in CHROME_CANDIDATES:
        p = shutil.which(c) or (c if os.path.exists(c) else None)
        if p:
            return p
    return None


def file_url(path):
    return Path(path).resolve().as_uri()


def render_playwright(html_path, out, w, h):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        chrome = find_chrome()
        try:
            browser = p.chromium.launch()
        except Exception:
            if not chrome:
                raise
            browser = p.chromium.launch(executable_path=chrome)
        page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        page.goto(file_url(html_path))
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts && document.fonts.ready")
        page.screenshot(path=out, clip={"x": 0, "y": 0, "width": w, "height": h})
        browser.close()


def render_chrome(html_path, out, w, h):
    chrome = find_chrome()
    if not chrome:
        raise RuntimeError("No Chrome/Chromium/Edge found")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([
            chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", f"--user-data-dir={tmp}",
            f"--window-size={w},{h}", "--force-device-scale-factor=1",
            f"--screenshot={os.path.abspath(out)}",
            file_url(html_path),
        ], check=True, capture_output=True, timeout=60)


def render(html, out, w, h):
    errors = []
    for fn in (render_playwright, render_chrome):
        try:
            fn(html, out, w, h)
            break
        except Exception as e:  # try the next renderer
            errors.append(f"{fn.__name__}: {e}")
    else:
        raise RuntimeError("Rendering failed:\n" + "\n".join(errors))

    try:
        from PIL import Image
        with Image.open(out) as im:
            size = im.size
            if size != (w, h):
                im.convert("RGB").resize((w, h)).save(out)
                size = (w, h)
        return f"OK {out} {size[0]}x{size[1]}"
    except ImportError:
        return f"OK {out} (expected {w}x{h})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("out")
    ap.add_argument("--format", choices=FORMATS.keys())
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    a = ap.parse_args()
    if a.format:
        w, h = FORMATS[a.format]
    elif a.width and a.height:
        w, h = a.width, a.height
    else:
        sys.exit("Give --format or both --width and --height")
    try:
        print(render(a.html, a.out, w, h))
    except RuntimeError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
