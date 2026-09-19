"""STRESS TEST - many requests back-to-back (Day 8 + Phase 7).

Sends N screenshots in a row to the running VLM server and checks that:
  no request fails, latency does not creep up, VRAM does not keep growing,
  and the server is still healthy at the end (no restart needed).
Run: .venv\\Scripts\\python.exe scripts\\stress_test.py          (50 requests)
     .venv\\Scripts\\python.exe scripts\\stress_test.py 200
"""
from __future__ import annotations

import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, banner, ensure_server_running, fail, ok, pause_if_double_clicked, warn  # noqa: E402

from models import config  # noqa: E402
from models.vlm_client import ask_vlm_detailed, server_is_up  # noqa: E402
from models.vram_monitor import used_mb  # noqa: E402

PROMPTS = ["Describe this web page in one sentence.",
           'Find the "Login button" in this screenshot. Answer ONLY with JSON: {"bbox_2d": [x1, y1, x2, y2]}']


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    banner(f"STRESS TEST - {n} requests back-to-back")
    if not ensure_server_running():
        fail("server not running")
        return 1
    images = sorted((ROOT / "test_images" / "720p").glob("*.png"))
    if not images:
        from make_test_images import make_synthetic
        make_synthetic()
        images = sorted((ROOT / "test_images" / "720p").glob("*.png"))
    lat, errors, vram = [], [], []
    t0 = time.time()
    for i in range(n):
        try:
            r = ask_vlm_detailed(images[i % len(images)], PROMPTS[i % 2], max_tokens=60, record_metric=False)
            lat.append(r["ms"])
            print(".", end="", flush=True)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"#{i + 1}: {type(exc).__name__}: {exc}")
            print("x", end="", flush=True)
        if i % 10 == 0:
            vram.append(used_mb() or 0)
    print()
    healthy = server_is_up()
    first, last = lat[:10], lat[-10:]
    L = [f"# Stress test - {datetime.now():%Y-%m-%d %H:%M}", "",
         f"- Requests: {n}, succeeded: {len(lat)}, failed: {len(errors)}",
         f"- Total time: {time.time() - t0:.0f} s",
         f"- Latency avg {statistics.mean(lat):.0f} ms, min {min(lat):.0f}, max {max(lat):.0f}" if lat else "- no successful requests",
         f"- First 10 avg {statistics.mean(first):.0f} ms vs last 10 avg {statistics.mean(last):.0f} ms" if lat else "",
         f"- VRAM samples (MB): {vram}",
         f"- Server healthy at the end: {'YES' if healthy else 'NO'}", ""]
    if errors:
        L += ["## Errors", *errors[:20]]
    out = config.RESULTS_DIR / "stress_test.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[2:8]))
    if errors or not healthy:
        warn("Problems found - see the Troubleshooting part of the guide.")
    else:
        ok("No crashes, server still healthy. PASSED.")
    if vram and max(vram) - min(vram) > 300:
        warn("VRAM grew by more than 300 MB during the test - mention it to the team.")
    ok(f"Saved {out}")
    return 0 if not errors and healthy else 1


if __name__ == "__main__":
    code = main()
    pause_if_double_clicked()
    sys.exit(code)
