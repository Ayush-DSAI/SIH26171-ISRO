"""DEMO PRE-WARM - run this 10 minutes before the demo (Day 10).

Starts the server if needed, runs 3 warm-up answers so the first real one is fast,
and checks the laptop is ready: charger plugged in, GPU awake, VRAM OK.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, banner, ensure_server_running, fail, ok, pause_if_double_clicked, warn  # noqa: E402

from models.vlm_client import ask_vlm_detailed  # noqa: E402
from models.vram_monitor import get_vram_mb  # noqa: E402


def main() -> int:
    banner("DEMO PRE-WARM")
    if not ensure_server_running():
        fail("Server could not start - switch to the backup video and see Troubleshooting.")
        return 1
    images = sorted((ROOT / "test_images" / "720p").glob("synth_*.png"))
    if not images:
        from make_test_images import make_synthetic
        make_synthetic()
        images = sorted((ROOT / "test_images" / "720p").glob("synth_*.png"))
    times = []
    for i in range(3):
        r = ask_vlm_detailed(images[i % len(images)], "Describe this web page in one sentence.", max_tokens=40,
                             timeout_s=60, record_metric=False)
        times.append(r["ms"])
        print(f"  warm-up {i + 1}: {r['ms']:.0f} ms")
    ok(f"Warm latency now: {times[-1]:.0f} ms")

    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery is not None and not battery.power_plugged:
            warn("CHARGER NOT PLUGGED IN! The GPU runs much slower on battery. Plug it in now.")
        elif battery is not None:
            ok(f"Charger plugged in (battery {battery.percent:.0f}%)")
    except Exception:  # noqa: BLE001
        pass
    gpu = get_vram_mb()
    if gpu and gpu["used_mb"] is not None:
        ok(f"{gpu['name']}: VRAM {gpu['used_mb']} / {gpu['total_mb']} MB, {gpu['temp_c']:.0f} C, power state {gpu['pstate']}")
        if gpu["used_mb"] > 0.9 * gpu["total_mb"]:
            warn("VRAM almost full - close games, Chrome tabs with video, and other GPU apps.")
    print("\n  Final checklist:")
    for item in ["Power mode = Performance (press Fn+Q until the power-button light is RED)",
                 "Charger plugged in", "Close games / video apps / extra browser tabs",
                 "Keep the 'VLM SERVER' window open (minimise it, don't close it)",
                 "Open the live GPU meter (START-HERE option 9) for the jury"]:
        print(f"   [ ] {item}")
    if times[-1] > 1500:
        warn("Still slow (>1.5 s). Check Performance mode + charger, then run this again.")
    return 0


if __name__ == "__main__":
    code = main()
    pause_if_double_clicked()
    sys.exit(code)
