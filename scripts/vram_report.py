"""VRAM REPORT - where every megabyte of GPU memory goes (Day 3 + Day 9, PPT evidence #6).

Starts its own temporary llama-server so it can measure:
  before the model loads -> after it loads (at rest) -> peak while reading a 720p and a 1080p screenshot.
Writes results/vram_report.md (component table for Experiment 4) and
results/nvidia_smi_during_inference.txt (take a screenshot of it for the PPT).
Close the normal VLM server window first.
"""
from __future__ import annotations

import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DESCRIBE_PROMPT, ROOT, TempServer, ask_raw, banner, fail, ok, pause_if_double_clicked, warn  # noqa: E402

from models import config  # noqa: E402
from models.vlm_client import server_is_up  # noqa: E402
from models.vram_monitor import VramPoller, get_vram_mb, used_mb  # noqa: E402


def main() -> int:
    banner("VRAM REPORT")
    if server_is_up():
        warn("The normal VLM server is running. Close its window (Ctrl+C) so we can measure 'before loading'.")
        input("  Press Enter when it is closed...")
    gpu = get_vram_mb()
    if not gpu or gpu["used_mb"] is None:
        fail("nvidia-smi is not working - update the NVIDIA driver (see guide).")
        return 1
    total = gpu["total_mb"]
    time.sleep(1)
    before = used_mb()
    model, mmproj = Path(config.MODEL_PATH), Path(config.MMPROJ_PATH)
    img720 = sorted((ROOT / "test_images" / "720p").glob("*.png"))[:3]
    img1080 = sorted((ROOT / "test_images" / "1080p").glob("*.png"))[:3]
    if not img720:
        from make_test_images import make_synthetic
        make_synthetic()
        img720 = sorted((ROOT / "test_images" / "720p").glob("*.png"))[:3]
        img1080 = sorted((ROOT / "test_images" / "1080p").glob("*.png"))[:3]

    with TempServer(str(model), ctx=config.CTX_SIZE, log_name="llama_server_vram.log") as srv:
        time.sleep(3)
        rest = used_mb()
        peaks = {}
        for label, imgs in (("720p", img720), ("1080p", img1080)):
            with VramPoller(0.05) as poll:
                for img in imgs:
                    ask_raw(srv.url, img, DESCRIBE_PROMPT, max_tokens=60)
            peaks[label] = poll.peak_mb
        # snapshot of nvidia-smi taken WHILE the model is busy, for the PPT
        busy = threading.Thread(target=ask_raw, args=(srv.url, (img1080 or img720)[0], DESCRIBE_PROMPT, 150))
        busy.start()
        time.sleep(0.3)
        smi = subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout
        busy.join()
        (config.RESULTS_DIR / "nvidia_smi_during_inference.txt").write_text(smi, encoding="utf-8")
        mem_lines = srv.memory_lines()

    model_mb = model.stat().st_size / 2**20
    mmproj_mb = mmproj.stat().st_size / 2**20
    loaded = rest - before
    buffers = max(0.0, loaded - model_mb - mmproj_mb)
    peak = max(v for v in peaks.values() if v is not None)
    rows = [
        ("Other programs + Windows (before model loads)", before),
        (f"Qwen3.5-4B {model.stem.split('-')[-1]} weights (file size)", model_mb),
        ("Vision encoder + projector - mmproj (file size)", mmproj_mb),
        (f"KV cache ({config.CTX_SIZE} ctx) + compute buffers (measured remainder)", buffers),
        ("Extra while reading a 1080p screenshot (peak - rest)", max(0, (peaks.get('1080p') or rest) - rest)),
    ]
    L = [f"# VRAM report - {gpu['name']}", "", f"Generated {datetime.now():%Y-%m-%d %H:%M}.", "",
         "| Component | VRAM (MB) | % of GPU |", "|---|---|---|"]
    for name, mb in rows:
        L.append(f"| {name} | {mb:,.0f} | {100 * mb / total:.1f}% |")
    L += [f"| **TOTAL at peak** | **{peak:,}** | **{100 * peak / total:.1f}%** |",
          f"| Remaining headroom | {total - peak:,} | {100 * (total - peak) / total:.1f}% |", "",
          f"- GPU total: {total:,} MB", f"- Before loading: {before:,} MB", f"- Model loaded, idle: {rest:,} MB",
          f"- Peak while reading 720p screenshots: {peaks.get('720p'):,} MB",
          f"- Peak while reading 1080p screenshots: {peaks.get('1080p') or 0:,} MB",
          f"- **Our model itself uses about {loaded:,} MB at rest and {peak - before:,} MB at peak.**", "",
          "## llama-server's own memory lines", "", "```", *(mem_lines or ["(not found)"]), "```", ""]
    out = config.RESULTS_DIR / "vram_report.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[4:14]))
    ok(f"Saved {out}")
    ok("Saved results/nvidia_smi_during_inference.txt")
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception as exc:  # noqa: BLE001
        fail(f"{type(exc).__name__}: {exc}")
        code = 1
    pause_if_double_clicked()
    sys.exit(code)
