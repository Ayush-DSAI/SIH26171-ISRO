"""SMOKE TEST - "Is my VLM alive and can it see?"  (Day 1-2 check + PPT evidence #2)

1. Starts llama-server if it is not already running.
2. Asks the model to describe a test screenshot.
3. Asks it where the Login button is, checks the answer against the known
   position, draws the box, saves results/smoke_grounding.png and opens it.
4. Writes results/curl_request.json so you can also test with curl (curl_test.bat).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (DESCRIBE_PROMPT, GROUNDING_PROMPT, IS_WINDOWS, ROOT, banner, center_inside,  # noqa: E402
                     ensure_server_running, fail, interpret_box, ok, parse_four_numbers,
                     pause_if_double_clicked, warn)

from PIL import Image, ImageDraw  # noqa: E402

from models import config  # noqa: E402
from models.vlm_client import ask_vlm_detailed, build_payload  # noqa: E402
from models.vram_monitor import get_vram_mb  # noqa: E402


def main() -> int:
    banner("SMOKE TEST - is the local VLM working?")
    if not ensure_server_running():
        fail("Server did not start. Look at the server window for a red error, then see the guide's Troubleshooting.")
        return 1
    ok(f"llama-server is up at {config.LLAMA_SERVER_URL}")

    truth_file = ROOT / "test_images" / "ground_truth.json"
    if not truth_file.exists():
        from make_test_images import make_synthetic
        make_synthetic()
    truth = json.loads(truth_file.read_text())
    key = "720p/synth_01.png"
    image_path = ROOT / "test_images" / key
    gt = truth[key]

    print("\n  Q1: " + DESCRIBE_PROMPT)
    first = ask_vlm_detailed(image_path, DESCRIBE_PROMPT, max_tokens=80, timeout_s=60)
    print(f"  A1: {first['text']}")
    print(f"      ({first['ms']:.0f} ms - the very first answer is slower, that's normal)")

    again = ask_vlm_detailed(image_path, DESCRIBE_PROMPT, max_tokens=80, timeout_s=30)
    ok(f"Second answer took {again['ms']:.0f} ms  (image+prompt {again['prompt_tokens']} tokens, "
       f"answer {again['completion_tokens']} tokens)")

    prompt = GROUNDING_PROMPT.format(target=gt["target"])
    print(f"\n  Q2: {prompt}")
    ground = ask_vlm_detailed(image_path, prompt, max_tokens=60, timeout_s=30)
    print(f"  A2: {ground['text']}   ({ground['ms']:.0f} ms)")

    nums = parse_four_numbers(ground["text"])
    img = Image.open(image_path).convert("RGB")
    d = ImageDraw.Draw(img)
    x, y, w, h = gt["bbox"]
    d.rectangle([x, y, x + w, y + h], outline="#22c55e", width=4)  # green = real position
    verdict = "no coordinates found in the answer"
    if nums:
        boxes = interpret_box(nums, gt["width"], gt["height"])
        hits = [name for name, b in boxes.items() if center_inside(b, gt["bbox"])]
        best = boxes[hits[0]] if hits else boxes["norm1000_xyxy"]
        bx, by, bw, bh = best
        d.rectangle([bx, by, bx + bw, by + bh], outline="#ef4444", width=4)  # red = model's answer
        if hits:
            verdict = f"CORRECT - the model's box is on the button (coordinate style: {hits[0]})"
            ok(verdict)
            if hits[0] == "norm1000_xyxy":
                print("         -> Tell Aditi: Qwen3.5 answers on a 0-1000 scale. Pixel x = value / 1000 * image width.")
        else:
            verdict = "model answered, but the box is not on the button (grounding needs better prompts - Aditi's job)"
            warn(verdict)
    else:
        warn(verdict)
    out = config.RESULTS_DIR / "smoke_grounding.png"
    img.save(out)
    ok(f"Saved picture: {out}  (green = real button, red = model's answer)")

    payload = build_payload(image_path, DESCRIBE_PROMPT, max_tokens=60)
    (config.RESULTS_DIR / "curl_request.json").write_text(json.dumps(payload))
    ok("Saved results/curl_request.json for the curl test (scripts/curl_test.bat)")

    vram = get_vram_mb()
    if vram and vram["used_mb"] is not None:
        ok(f"GPU: {vram['name']}  VRAM used {vram['used_mb']} MB of {vram['total_mb']} MB")

    report = config.RESULTS_DIR / "smoke_test.txt"
    report.write_text(
        f"Describe answer: {first['text']}\nWarm latency: {again['ms']} ms\n"
        f"Grounding answer: {ground['text']}\nVerdict: {verdict}\n"
        f"VRAM: {vram['used_mb'] if vram else 'n/a'} MB\n", encoding="utf-8")
    banner("SMOKE TEST PASSED - your local VLM works!")
    if IS_WINDOWS:
        os.startfile(out)  # type: ignore[attr-defined]
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception as exc:  # noqa: BLE001
        fail(f"{type(exc).__name__}: {exc}")
        code = 1
    pause_if_double_clicked()
    sys.exit(code)
