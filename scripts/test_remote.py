"""REMOTE MODEL TEST (Day 7). Checks the cloud model call and the privacy guards.

1. Makes a pretend-sanitized screenshot (black boxes over the form fields).
2. Shows that a NON-sanitized file is refused (privacy guard).
3. Sends the sanitized one with a task and prints the answer + time,
   or the clearly-labelled MOCK answer if no API key is set yet.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, banner, fail, ok, pause_if_double_clicked, warn  # noqa: E402

import json  # noqa: E402

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from models import config  # noqa: E402
from models import remote_client  # noqa: E402


def make_fake_sanitized() -> Path:
    """Black boxes over the form fields + blurred avatar, like Abhishek's redact() would do."""
    truth_file = ROOT / "test_images" / "ground_truth.json"
    if not truth_file.exists() or "pii_boxes" not in json.loads(truth_file.read_text())["720p/synth_01.png"]:
        from make_test_images import make_synthetic
        make_synthetic()
    gt = json.loads(truth_file.read_text())["720p/synth_01.png"]
    img = Image.open(ROOT / "test_images" / "720p" / "synth_01.png").convert("RGB")
    d = ImageDraw.Draw(img)
    for item in gt["pii_boxes"]:
        x, y, w, h = [int(v) for v in item["bbox"]]
        if item["type"] == "face":
            region = img.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(12))
            img.paste(region, (x, y))
        else:
            d.rectangle([x, y, x + w, y + h], fill="black")
    out = config.RESULTS_DIR / "sanitized_test.png"
    img.save(out)
    return out


def main() -> int:
    banner("REMOTE MODEL TEST")
    print(f"  Provider: {config.REMOTE_PROVIDER}   Model: {config.REMOTE_MODEL_NAME}   "
          f"API key set: {'yes' if config.REMOTE_MODEL_API_KEY else 'NO (mock mode)'}")
    sanitized = make_fake_sanitized()
    ok(f"Made test image {sanitized.name}")

    raw = ROOT / "test_images" / "720p" / "synth_01.png"
    try:
        remote_client.ask_remote(str(raw), "Click the Login button")
        fail("Privacy guard did NOT stop a raw screenshot!")
    except remote_client.NotSanitizedError:
        ok("Privacy guard works: a raw screenshot was refused.")

    print("  Task text masking example:",
          remote_client.mask_text_pii("Login as rahul@example.com, phone 9876543210"))

    result = remote_client.ask_remote_detailed(str(sanitized), "Log in to this website")
    if result["mocked"]:
        warn(f"MOCKED answer (reason: {result['reason']})")
    else:
        ok(f"REAL answer from {result['model']} in {result['ms']:.0f} ms")
    print(f"\n  Remote model says: {result['text']}\n")
    return 0


if __name__ == "__main__":
    code = main()
    pause_if_double_clicked()
    sys.exit(code)
