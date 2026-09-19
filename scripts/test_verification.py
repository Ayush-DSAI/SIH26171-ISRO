"""VERIFICATION TEST (Day 4). Shows verify_action() telling 'page changed' from 'nothing happened'.

Case A: login page -> "Welcome!" page                       expected changed = True
Case B: login page -> same page with a tiny cursor blink     expected changed = False
Case C: login page -> same page, Login button turned darker  expected changed = True, target_changed = True
Saves results/verification_demo.png (before | after | red = pixels that changed).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, banner, fail, ok, pause_if_double_clicked  # noqa: E402

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from models import config  # noqa: E402
from models.verification import verify_action  # noqa: E402


def main() -> int:
    banner("VERIFICATION TEST")
    truth_file = ROOT / "test_images" / "ground_truth.json"
    if not (ROOT / "test_images" / "after_click_720p.png").exists():
        from make_test_images import make_synthetic
        make_synthetic()
    gt = json.loads(truth_file.read_text())["720p/synth_01.png"]
    before = Image.open(ROOT / "test_images" / "720p" / "synth_01.png").convert("RGB")
    after_page = Image.open(ROOT / "test_images" / "after_click_720p.png").convert("RGB")

    blink = before.copy()
    x, y, w, h = gt["pii_boxes"][1]["bbox"]
    ImageDraw.Draw(blink).line([x + 100, y + 8, x + 100, y + h - 8], fill="black", width=2)

    pressed = before.copy()
    bx, by, bw, bh = gt["bbox"]
    ImageDraw.Draw(pressed).rectangle([bx, by, bx + bw, by + bh], fill="#0b1f4d")

    cases = [("A: page changed to 'Welcome'", after_page, True, None),
             ("B: only a cursor blinked", blink, False, None),
             ("C: the Login button reacted", pressed, True, gt["bbox"])]
    all_good = True
    for name, after, expected, target in cases:
        r = verify_action(before, after, target_bbox=target)
        good = r["changed"] == expected and (target is None or r["target_changed"])
        all_good &= good
        (ok if good else fail)(f"{name}: changed={r['changed']} (expected {expected}), "
                               f"pixels changed={r['changed_fraction']:.2%}, SSIM={r['ssim']}, "
                               f"target_changed={r['target_changed']}, {r['ms']} ms")

    a, b = np.asarray(before, dtype=np.int16), np.asarray(after_page, dtype=np.int16)
    mask = np.abs(a - b).max(axis=2) > 25
    overlay = np.asarray(before).copy()
    overlay[mask] = [239, 68, 68]
    strip = Image.new("RGB", (1280 * 3 // 2, 240), "white")
    for i, im in enumerate([before, after_page, Image.fromarray(overlay)]):
        strip.paste(im.resize((640, 360)).resize((426, 240)), (i * 426 + i * 5, 0))
    out = config.RESULTS_DIR / "verification_demo.png"
    strip.save(out)
    ok(f"Saved {out}")
    return 0 if all_good else 1


if __name__ == "__main__":
    code = main()
    pause_if_double_clicked()
    sys.exit(code)
