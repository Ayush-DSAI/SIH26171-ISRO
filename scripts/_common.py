"""Shared helpers for the scripts in this folder (you don't run this file directly)."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models import config  # noqa: E402

IS_WINDOWS = sys.platform == "win32"

GROUNDING_PROMPT = (
    'Find the "{target}" in this screenshot. Answer ONLY with JSON in this exact form: '
    '{{"bbox_2d": [x1, y1, x2, y2]}}'
)
DESCRIBE_PROMPT = "Describe this web page in one sentence."


def banner(text: str) -> None:
    line = "=" * max(60, len(text) + 4)
    print(f"\n{line}\n  {text}\n{line}")


def ok(text: str) -> None:
    print(f"  [OK]   {text}")


def warn(text: str) -> None:
    print(f"  [!!]   {text}")


def fail(text: str) -> None:
    print(f"  [FAIL] {text}")


def pause_if_double_clicked() -> None:
    if IS_WINDOWS and os.environ.get("SHAURYA_MENU") != "1":
        input("\nPress Enter to close...")


# ------------------------------------------------------------------ coordinates
def parse_four_numbers(text: str) -> list[float] | None:
    """First 4 numbers of the answer, ignoring words like 'bbox_2d' that contain digits."""
    inside = re.search(r"\[([^\[\]]*)\]", text)
    candidates = [inside.group(1)] if inside else []
    candidates.append(re.sub(r"[A-Za-z_]+\d+[A-Za-z_]*", " ", text))
    for chunk in candidates:
        nums = re.findall(r"-?\d+(?:\.\d+)?", chunk)
        if len(nums) >= 4:
            return [float(n) for n in nums[:4]]
    return None


def interpret_box(nums: list[float], width: int, height: int) -> dict:
    """The same 4 numbers read in the 3 common ways -> pixel boxes [x, y, w, h]."""
    x1, y1, x2, y2 = nums
    return {
        "pixel_xyxy": [x1, y1, x2 - x1, y2 - y1],
        "norm1000_xyxy": [x1 / 1000 * width, y1 / 1000 * height, (x2 - x1) / 1000 * width, (y2 - y1) / 1000 * height],
        "pixel_xywh": [x1, y1, x2, y2],
    }


def center_inside(box: list[float], truth: list[float]) -> bool:
    cx, cy = box[0] + box[2] / 2, box[1] + box[3] / 2
    tx, ty, tw, th = truth
    return tx <= cx <= tx + tw and ty <= cy <= ty + th


# ------------------------------------------------------------------ llama-server process control
def server_command(model: str, port: int, ctx: int, host: str = "127.0.0.1", webui: bool = False) -> list[str]:
    cmd = [config.LLAMA_SERVER_EXE, "-m", model, "--mmproj", config.MMPROJ_PATH,
           "--host", host, "--port", str(port), "-c", str(ctx), "-ngl", str(config.N_GPU_LAYERS), "-np", "1"]
    if not webui:
        cmd.append("--no-webui")
    return cmd


class TempServer:
    """Starts llama-server in the background for a test, stops it afterwards."""

    def __init__(self, model: str, port: int = 8099, ctx: int = 4096, log_name: str = "llama_server_test.log"):
        self.model, self.port, self.ctx = model, port, ctx
        self.url = f"http://127.0.0.1:{port}"
        self.log_path = config.RESULTS_DIR / log_name
        self.proc: subprocess.Popen | None = None
        self.load_seconds: float | None = None

    def __enter__(self) -> "TempServer":
        from models.vlm_client import wait_for_server
        if not Path(config.LLAMA_SERVER_EXE).exists():
            raise FileNotFoundError(f"llama-server not found at {config.LLAMA_SERVER_EXE} - run setup first")
        if not Path(self.model).exists():
            raise FileNotFoundError(f"Model file not found: {self.model}")
        self._log = open(self.log_path, "w", encoding="utf-8", errors="replace")
        flags = 0x08000000 if IS_WINDOWS else 0  # CREATE_NO_WINDOW
        start = time.perf_counter()
        self.proc = subprocess.Popen(server_command(self.model, self.port, self.ctx),
                                     stdout=self._log, stderr=subprocess.STDOUT, creationflags=flags)
        deadline = time.time() + 240
        while time.time() < deadline:
            if self.proc.poll() is not None:
                self._log.flush()
                raise RuntimeError(f"llama-server stopped while loading. See {self.log_path}")
            if wait_for_server(1, self.url):
                self.load_seconds = round(time.perf_counter() - start, 1)
                return self
        raise TimeoutError(f"llama-server did not become ready in 4 minutes. See {self.log_path}")

    def __exit__(self, *exc) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self._log.close()
        time.sleep(2)  # let the driver release the memory

    def memory_lines(self) -> list[str]:
        """llama-server prints its own memory use ('... buffer size = 123.45 MiB')."""
        try:
            text = self.log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return []
        keep = [ln.strip() for ln in text.splitlines()
                if re.search(r"buffer size\s*=|model size|CLIP using|offloaded \d+/\d+ layers", ln)]
        return keep[:40]


def ask_raw(url: str, image, prompt: str, max_tokens: int = 128, timeout_s: float = 60) -> dict:
    """One request to a specific server URL without the retry logic (used for benchmarks)."""
    import httpx
    from models.vlm_client import _parse, build_payload
    payload = build_payload(image, prompt, max_tokens=max_tokens, temperature=0.0, cache_prompt=False)
    start = time.perf_counter()
    r = httpx.post(f"{url}/v1/chat/completions", json=payload, timeout=timeout_s)
    wall = (time.perf_counter() - start) * 1000
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    out = _parse(r.json())
    out["ms"] = round(wall, 1)
    return out


def ensure_server_running(timeout_s: int = 240) -> bool:
    """If the main server (port from .env) is not running, open it in a new window and wait."""
    from models.vlm_client import server_is_up, wait_for_server
    if server_is_up():
        return True
    print("  The VLM server is not running - starting it for you in a new window...")
    bat = ROOT / "scripts" / "start_llama_server.bat"
    if IS_WINDOWS and bat.exists():
        subprocess.Popen(["cmd", "/c", "start", "VLM SERVER - keep this window open", str(bat)], cwd=str(ROOT))
    else:
        warn("Please start llama-server yourself (START-HERE option 2).")
    print("  Waiting for the model to load (usually 10-60 seconds)", end="", flush=True)
    end = time.time() + timeout_s
    while time.time() < end:
        if wait_for_server(2):
            print(" ready!")
            return True
        print(".", end="", flush=True)
    print()
    return False
