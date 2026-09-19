"""Reads settings from the .env file so every script uses the same values.

You never need to edit this file. Change settings in the `.env` file instead.
"""
from __future__ import annotations

import os
from pathlib import Path

# The kit/repo root is the folder that contains the "models" folder.
ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
TEST_IMAGES_DIR = ROOT / "test_images"


def _load_env_file() -> None:
    """Tiny .env reader (no extra package needed). Real environment variables win."""
    for candidate in (ROOT / ".env", Path.cwd() / ".env"):
        if candidate.is_file():
            for raw in candidate.read_text(encoding="utf-8-sig").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key, value = key.strip(), value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)
            break


_load_env_file()


def get(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def get_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, default))
    except ValueError:
        return default


def get_float(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, default))
    except ValueError:
        return default


# ---- Local VLM (llama-server) ----
LLAMA_SERVER_URL = get("LLAMA_SERVER_URL", "http://127.0.0.1:8081").rstrip("/")
LLAMA_API_KEY = get("LLAMA_API_KEY", "")            # only needed if you shared the server with --api-key
VLM_MODEL_NAME = get("VLM_MODEL_NAME", "qwen3.5-4b")  # llama-server ignores it, Ollama needs it
VLM_TIMEOUT_S = get_float("VLM_TIMEOUT_S", 10.0)     # contract: raise TimeoutError after 10 s
VLM_MAX_RETRIES = get_int("VLM_MAX_RETRIES", 2)      # Day 5: max 2 retries

LLAMA_SERVER_EXE = get("LLAMA_SERVER_EXE", str(ROOT / "llama" / "llama-server.exe"))
MODEL_PATH = get("MODEL_PATH", str(ROOT / "weights" / "Qwen3.5-4B-Q4_K_M.gguf"))
MMPROJ_PATH = get("MMPROJ_PATH", str(ROOT / "weights" / "mmproj-F16.gguf"))
CTX_SIZE = get_int("CTX_SIZE", 4096)
N_GPU_LAYERS = get_int("N_GPU_LAYERS", 99)

# ---- Remote model ----
REMOTE_PROVIDER = get("REMOTE_PROVIDER", "gemini").lower()   # gemini | openai | custom | mock
REMOTE_MODEL_API_KEY = get("REMOTE_MODEL_API_KEY", "")
REMOTE_MODEL_URL = get(
    "REMOTE_MODEL_URL",
    "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
)
REMOTE_MODEL_NAME = get("REMOTE_MODEL_NAME", "gemini-3.5-flash")
REMOTE_TIMEOUT_S = get_float("REMOTE_TIMEOUT_S", 8.0)
REMOTE_MAX_RETRIES = get_int("REMOTE_MAX_RETRIES", 2)

RESULTS_DIR.mkdir(exist_ok=True)
