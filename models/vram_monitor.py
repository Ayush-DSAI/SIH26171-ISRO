"""GPU memory (VRAM) helpers built on `nvidia-smi` (it comes with the NVIDIA driver).

Use in code:
    from models.vram_monitor import get_vram_mb, VramPoller
    print(get_vram_mb())                 # e.g. {'used_mb': 4210, 'total_mb': 8188, ...}
    with VramPoller() as p:              # samples every 100 ms in the background
        ...do an inference...
    print(p.peak_mb)

Live meter for the demo (run from the kit folder):
    .venv\\Scripts\\python.exe -m models.vram_monitor
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
import time
from typing import Optional

_QUERY = "memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw,pstate,name"
_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0  # stop a console window flashing on Windows


def _nvidia_smi() -> Optional[str]:
    exe = shutil.which("nvidia-smi")
    if exe:
        return exe
    fallback = r"C:\Windows\System32\nvidia-smi.exe"
    return fallback if sys.platform == "win32" and os.path.exists(fallback) else None


def get_vram_mb() -> Optional[dict]:
    """Return current GPU stats, or None if nvidia-smi is not available."""
    exe = _nvidia_smi()
    if not exe:
        return None
    try:
        out = subprocess.run(
            [exe, f"--query-gpu={_QUERY}", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5, creationflags=_NO_WINDOW,
        ).stdout.strip().splitlines()[0]
    except Exception:
        return None
    parts = [p.strip() for p in out.split(",")]

    def num(value: str) -> Optional[float]:
        try:
            return float(value)
        except ValueError:
            return None  # e.g. "[N/A]"

    used, total = num(parts[0]), num(parts[1])
    return {
        "used_mb": int(used) if used is not None else None,
        "total_mb": int(total) if total is not None else None,
        "gpu_util_pct": num(parts[2]),
        "temp_c": num(parts[3]),
        "power_w": num(parts[4]),
        "pstate": parts[5] if len(parts) > 5 else None,
        "name": parts[6] if len(parts) > 6 else None,
    }


def used_mb() -> Optional[int]:
    info = get_vram_mb()
    return info["used_mb"] if info else None


class VramPoller:
    """Samples VRAM every `interval_s` seconds in a background thread and keeps the peak."""

    def __init__(self, interval_s: float = 0.1):
        self.interval_s = interval_s
        self.samples: list[tuple[float, int]] = []
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _run(self) -> None:
        start = time.perf_counter()
        while not self._stop.is_set():
            value = used_mb()
            if value is not None:
                self.samples.append((time.perf_counter() - start, value))
            self._stop.wait(self.interval_s)

    def start(self) -> "VramPoller":
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=6)

    def __enter__(self) -> "VramPoller":
        return self.start()

    def __exit__(self, *exc) -> None:
        self.stop()

    @property
    def peak_mb(self) -> Optional[int]:
        return max((v for _, v in self.samples), default=None)

    @property
    def avg_mb(self) -> Optional[float]:
        return sum(v for _, v in self.samples) / len(self.samples) if self.samples else None


def live_meter(interval_s: float = 0.5) -> None:
    """Prints a live VRAM bar. Press Ctrl+C to stop."""
    print("Live GPU meter - press Ctrl+C to stop\n")
    peak = 0
    try:
        while True:
            info = get_vram_mb()
            if not info or info["used_mb"] is None:
                print("nvidia-smi not found - is the NVIDIA driver installed?")
                return
            used, total = info["used_mb"], info["total_mb"] or 8192
            peak = max(peak, used)
            filled = int(30 * used / total)
            bar = "#" * filled + "-" * (30 - filled)
            line = (f"VRAM {used/1024:4.1f} GB / {total/1024:.1f} GB [{bar}]  peak {peak/1024:.1f} GB  "
                    f"GPU {info['gpu_util_pct'] or 0:3.0f}%  {info['temp_c'] or 0:.0f}C  {info['pstate'] or ''}")
            print("\r" + line, end="", flush=True)
            time.sleep(interval_s)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    live_meter()
