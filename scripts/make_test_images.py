"""Creates the test screenshots used by the smoke test and the benchmark.

  * 10 synthetic "fake website" screenshots per resolution (720p + 1080p) where we
    KNOW exactly where the button is (ground truth) -> lets us score accuracy.
    Also an 'after click' page for the verification test.
  * Up to 10 real website screenshots per resolution (needs internet + Playwright).

Run:  .venv\\Scripts\\python.exe scripts\\make_test_images.py          (synthetic + real)
      .venv\\Scripts\\python.exe scripts\\make_test_images.py --no-web (synthetic only)
All images are FAKE data - no real people or real personal numbers.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, banner, ok, pause_if_double_clicked, warn  # noqa: E402

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

OUT = ROOT / "test_images"
RESOLUTIONS = {"720p": (1280, 720), "1080p": (1920, 1080)}
BUTTONS = [("Login", "#2563eb"), ("Sign in", "#16a34a"), ("Submit", "#dc2626"), ("Log in", "#7c3aed"),
           ("Continue", "#ea580c"), ("Login", "#0891b2"), ("Search", "#4f46e5"), ("Sign in", "#be123c"),
           ("Next", "#15803d"), ("Login", "#1d4ed8")]
SITES = ["https://www.google.com", "https://en.wikipedia.org/wiki/Indian_Space_Research_Organisation",
         "https://www.isro.gov.in", "https://github.com/login", "https://www.python.org",
         "https://news.ycombinator.com", "https://duckduckgo.com", "https://www.wikipedia.org",
         "https://stackoverflow.com/questions", "https://www.bing.com", "https://www.bbc.com/news",
         "https://www.amazon.in"]


def font(size: int) -> ImageFont.ImageFont:
    for name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def draw_login_page(width: int, height: int, idx: int, clicked: bool = False) -> tuple[Image.Image, dict]:
    rnd = random.Random(idx)
    s = width / 1280  # scale factor so 1080p looks the same, just sharper
    img = Image.new("RGB", (width, height), "#f3f4f6")
    d = ImageDraw.Draw(img)
    # top bar
    d.rectangle([0, 0, width, int(64 * s)], fill="#111827")
    d.text((int(24 * s), int(18 * s)), f"DemoPortal {idx + 1}", fill="white", font=font(int(26 * s)))
    for i, item in enumerate(["Home", "About", "Help"]):
        d.text((width - int((260 - i * 80) * s), int(22 * s)), item, fill="#d1d5db", font=font(int(18 * s)))
    # card position varies so the button is not always in the same place
    card_w, card_h = int(460 * s), int(470 * s)
    cx = int(rnd.uniform(0.12, 0.88 - card_w / width) * width)
    cy = int(rnd.uniform(0.14, 0.95 - card_h / height) * height)
    d.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=int(14 * s), fill="white", outline="#e5e7eb")
    if clicked:
        d.text((cx + int(40 * s), cy + int(180 * s)), "Welcome! You are logged in.", fill="#16a34a", font=font(int(28 * s)))
        return img, {}
    label, color = BUTTONS[idx % len(BUTTONS)]
    d.text((cx + int(32 * s), cy + int(24 * s)), "Account login", fill="#111827", font=font(int(28 * s)))
    # fake face avatar (simple cartoon, not a real person)
    ax, ay, r = cx + card_w - int(90 * s), cy + int(20 * s), int(30 * s)
    d.ellipse([ax, ay, ax + 2 * r, ay + 2 * r], fill="#fcd9b6", outline="#9ca3af")
    d.ellipse([ax + r * 0.55, ay + r * 0.7, ax + r * 0.75, ay + r * 0.9], fill="#374151")
    d.ellipse([ax + r * 1.25, ay + r * 0.7, ax + r * 1.45, ay + r * 0.9], fill="#374151")
    d.arc([ax + r * 0.6, ay + r * 1.0, ax + r * 1.4, ay + r * 1.5], 20, 160, fill="#374151", width=max(1, int(2 * s)))
    fields = [("Username", "rahul.demo"), ("Password", "••••••••"), ("Email", "rahul.demo@example.com")]
    pii_boxes = [{"type": "face", "bbox": [ax, ay, 2 * r, 2 * r]}]
    y = cy + int(90 * s)
    for name, value in fields:
        d.text((cx + int(32 * s), y), name, fill="#374151", font=font(int(18 * s)))
        x0, y0, x1, y1 = cx + int(32 * s), y + int(26 * s), cx + card_w - int(32 * s), y + int(66 * s)
        d.rounded_rectangle([x0, y0, x1, y1], radius=int(6 * s), fill="#f9fafb", outline="#d1d5db")
        d.text((cx + int(44 * s), y + int(35 * s)), value, fill="#111827", font=font(int(18 * s)))
        pii_boxes.append({"type": name.lower() + "_field", "bbox": [x0, y0, x1 - x0, y1 - y0]})
        y += int(90 * s)
    bw, bh = int(rnd.choice([140, 180, 396]) * s), int(46 * s)
    bx = cx + int(32 * s) if bw > int(300 * s) else cx + rnd.choice([int(32 * s), card_w - int(32 * s) - bw])
    by = y + int(4 * s)
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=int(8 * s), fill=color)
    f = font(int(20 * s))
    tw = d.textlength(label, font=f)
    d.text((bx + (bw - tw) / 2, by + int(12 * s)), label, fill="white", font=f)
    d.text((cx + int(32 * s), by + bh + int(14 * s)), "Forgot password?", fill="#2563eb", font=font(int(16 * s)))
    return img, {"target": f"{label} button", "bbox": [bx, by, bw, bh], "width": width, "height": height,
                 "pii_boxes": pii_boxes}


def make_synthetic() -> dict:
    truth: dict = {}
    for res, (w, h) in RESOLUTIONS.items():
        folder = OUT / res
        folder.mkdir(parents=True, exist_ok=True)
        for i in range(10):
            img, gt = draw_login_page(w, h, i)
            name = f"synth_{i + 1:02d}.png"
            img.save(folder / name)
            truth[f"{res}/{name}"] = gt
        after, _ = draw_login_page(w, h, 0, clicked=True)
        after.save(OUT / f"after_click_{res}.png")
    (OUT / "ground_truth.json").write_text(json.dumps(truth, indent=2))
    ok(f"20 synthetic screenshots + ground truth saved in {OUT}")
    return truth


def make_real(limit: int = 10) -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        warn("Playwright not installed - skipping real websites (synthetic ones are enough to start).")
        return 0
    saved = 0
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for url in SITES:
                if saved >= limit:
                    break
                name = "web_" + url.split("//")[1].split("/")[0].replace("www.", "").replace(".", "_") + ".png"
                try:
                    for res, (w, h) in RESOLUTIONS.items():
                        page = browser.new_page(viewport={"width": w, "height": h})
                        page.goto(url, wait_until="load", timeout=25000)
                        page.wait_for_timeout(1500)
                        page.screenshot(path=str(OUT / res / name))
                        page.close()
                    saved += 1
                    ok(f"captured {url}")
                except Exception as exc:  # noqa: BLE001
                    warn(f"skipped {url} ({type(exc).__name__})")
            browser.close()
    except Exception as exc:  # noqa: BLE001
        warn(f"Could not start the Playwright browser ({exc}). Run setup again or use --no-web.")
    return saved


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-web", action="store_true", help="only make synthetic images")
    args = ap.parse_args()
    banner("Making test screenshots")
    make_synthetic()
    if not args.no_web:
        n = make_real()
        ok(f"{n} real website screenshots per resolution")
    pause_if_double_clicked()
