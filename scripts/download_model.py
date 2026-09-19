"""Downloads Qwen3.5-4B GGUF files from Hugging Face (with resume + progress bar).

  .venv\\Scripts\\python.exe scripts\\download_model.py            -> Q4_K_M + mmproj (main files)
  .venv\\Scripts\\python.exe scripts\\download_model.py Q5_K_M     -> an extra quantization for the benchmark
  .venv\\Scripts\\python.exe scripts\\download_model.py Q8_0 Q6_K  -> several

Files come from https://huggingface.co/unsloth/Qwen3.5-4B-GGUF
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, banner, fail, ok, pause_if_double_clicked  # noqa: E402

import httpx  # noqa: E402

REPO = "https://huggingface.co/unsloth/Qwen3.5-4B-GGUF/resolve/main"
WEIGHTS = ROOT / "weights"
KNOWN_SIZES_GB = {"Q4_K_M": 2.74, "Q5_K_M": 3.14, "Q6_K": 3.53, "Q8_0": 4.48, "Q4_0": 2.58, "Q3_K_M": 2.29}


def file_for(quant: str) -> str:
    return "mmproj-F16.gguf" if quant.lower() == "mmproj" else f"Qwen3.5-4B-{quant}.gguf"


def is_complete_gguf(path: Path, min_mb: int = 300) -> bool:
    if not path.exists() or path.stat().st_size < min_mb * 1024 * 1024:
        return False
    with path.open("rb") as f:
        return f.read(4) == b"GGUF"


def download(quant: str) -> Path:
    WEIGHTS.mkdir(exist_ok=True)
    name = file_for(quant)
    dest = WEIGHTS / name
    part = dest.with_suffix(dest.suffix + ".part")
    if is_complete_gguf(dest):
        ok(f"{name} already downloaded")
        return dest
    url = f"{REPO}/{name}"
    for attempt in range(1, 6):
        have = part.stat().st_size if part.exists() else 0
        headers = {"Range": f"bytes={have}-"} if have else {}
        try:
            with httpx.stream("GET", url, headers=headers, follow_redirects=True, timeout=60) as r:
                if r.status_code == 416:  # already complete
                    break
                r.raise_for_status()
                total = int(r.headers.get("Content-Length", 0)) + (have if r.status_code == 206 else 0)
                mode = "ab" if r.status_code == 206 else "wb"
                done = have if r.status_code == 206 else 0
                t0, last = time.time(), 0.0
                with part.open(mode) as f:
                    for chunk in r.iter_bytes(1024 * 1024):
                        f.write(chunk)
                        done += len(chunk)
                        if time.time() - last > 0.5:
                            last = time.time()
                            speed = (done - have) / max(1e-6, last - t0) / 1e6
                            pct = 100 * done / total if total else 0
                            print(f"\r  {name}: {done/1e9:5.2f} / {total/1e9:5.2f} GB  ({pct:5.1f}%)  {speed:5.1f} MB/s   ",
                                  end="", flush=True)
            print()
            break
        except (httpx.HTTPError, OSError) as exc:
            print()
            fail(f"download interrupted ({exc}); retrying in 5 s (attempt {attempt}/5)")
            time.sleep(5)
    part.replace(dest) if part.exists() else None
    if not is_complete_gguf(dest):
        raise RuntimeError(f"{name} did not download correctly - check your internet and run again")
    ok(f"{name} saved ({dest.stat().st_size/1e9:.2f} GB)")
    return dest


if __name__ == "__main__":
    wanted = sys.argv[1:] or ["Q4_K_M", "mmproj"]
    banner("Downloading model files: " + ", ".join(wanted))
    for q in wanted:
        download(q)
    pause_if_double_clicked()
