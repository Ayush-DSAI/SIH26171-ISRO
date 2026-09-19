"""Client for the local VLM (Qwen3.5-4B running inside llama-server).

INTEGRATION CONTRACT (Shaurya -> Ayush), from the team plan:
    ask_vlm(image_path: str, prompt: str) -> str
        Sends image + prompt to llama-server. Returns the model's raw text.
        Raises TimeoutError if the server doesn't answer within 10 s.

Extras you can use:
    ask_vlm_detailed(...)  -> dict with text + timings (ms, tokens)
    ask_vlm_async(...)     -> same as ask_vlm but `await`-able (for async Playwright code)
    server_is_up()         -> True/False
    wait_for_server(60)    -> waits until the model is loaded

`image_path` may also be raw PNG/JPEG bytes (e.g. page.screenshot()) or a PIL image.
"""
from __future__ import annotations

import asyncio
import base64
import io
import re
import time
from pathlib import Path
from typing import Any, Optional, Union

import httpx

from models import config
from models.metrics import record

ImageLike = Union[str, Path, bytes, "Image.Image"]  # noqa: F821

_CHAT_URL = f"{config.LLAMA_SERVER_URL}/v1/chat/completions"
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


class VLMError(RuntimeError):
    """The server answered, but with an error or an empty response."""


# --------------------------------------------------------------------------- helpers
def _headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if config.LLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {config.LLAMA_API_KEY}"
    return headers


def image_to_data_uri(image: ImageLike, max_side: Optional[int] = None) -> str:
    """Turn a file path / bytes / PIL image into a base64 data URI the API understands."""
    mime = "image/png"
    if isinstance(image, (str, Path)):
        path = Path(image)
        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {path}")
        data = path.read_bytes()
        suffix = path.suffix.lower()
        mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(suffix, "image/png")
    elif isinstance(image, (bytes, bytearray)):
        data = bytes(image)
        if data[:3] == b"\xff\xd8\xff":
            mime = "image/jpeg"
    else:  # PIL image
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        data = buf.getvalue()

    if max_side:  # optional downscale (keeps aspect ratio)
        from PIL import Image

        img = Image.open(io.BytesIO(data))
        if max(img.size) > max_side:
            img.thumbnail((max_side, max_side))
            buf = io.BytesIO()
            img.convert("RGB").save(buf, format="PNG")
            data, mime = buf.getvalue(), "image/png"
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def build_payload(image: ImageLike, prompt: str, max_tokens: int = 256, temperature: float = 0.1,
                  system: Optional[str] = None, max_side: Optional[int] = None,
                  cache_prompt: bool = True) -> dict:
    messages: list[dict[str, Any]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": image_to_data_uri(image, max_side)}},
            {"type": "text", "text": prompt},
        ],
    })
    return {
        "model": config.VLM_MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.8,
        "top_k": 20,
        "stream": False,
        "cache_prompt": cache_prompt,
        # Qwen3.5 small models don't "think" by default; this makes sure (thinking = slow).
        "chat_template_kwargs": {"enable_thinking": False},
    }


def _parse(data: dict) -> dict:
    try:
        message = data["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        raise VLMError(f"Unexpected response from server: {str(data)[:300]}")
    text = (message.get("content") or "").strip()
    if not text:  # thinking accidentally on -> answer may sit in reasoning_content
        text = (message.get("reasoning_content") or "").strip()
    text = _THINK_RE.sub("", text).strip()
    if not text:
        raise VLMError("Server returned an empty answer")
    usage = data.get("usage") or {}
    timings = data.get("timings") or {}
    return {
        "text": text,
        "prompt_tokens": usage.get("prompt_tokens", timings.get("prompt_n")),
        "completion_tokens": usage.get("completion_tokens", timings.get("predicted_n")),
        "prompt_ms": timings.get("prompt_ms"),        # reading the image + prompt
        "predicted_ms": timings.get("predicted_ms"),  # writing the answer
        "tokens_per_second": timings.get("predicted_per_second"),
    }


def _not_running_message() -> str:
    return (f"Cannot reach llama-server at {config.LLAMA_SERVER_URL}. "
            "Start it first: double-click START-HERE.bat and choose option 2.")


# --------------------------------------------------------------------------- sync API
def ask_vlm_detailed(image_path: ImageLike, prompt: str, max_tokens: int = 256,
                     temperature: float = 0.1, system: Optional[str] = None,
                     timeout_s: Optional[float] = None, max_retries: Optional[int] = None,
                     max_side: Optional[int] = None, cache_prompt: bool = True,
                     record_metric: bool = True) -> dict:
    """Like ask_vlm but returns a dict: text, ms, tokens, attempts, ..."""
    timeout_s = config.VLM_TIMEOUT_S if timeout_s is None else timeout_s
    max_retries = config.VLM_MAX_RETRIES if max_retries is None else max_retries
    payload = build_payload(image_path, prompt, max_tokens, temperature, system, max_side, cache_prompt)

    deadline = time.perf_counter() + timeout_s
    start = time.perf_counter()
    last_error: Optional[BaseException] = None
    for attempt in range(1, max_retries + 2):
        remaining = deadline - time.perf_counter()
        if remaining <= 0.05:
            break
        try:
            with httpx.Client(timeout=httpx.Timeout(remaining, connect=min(3.0, remaining))) as client:
                response = client.post(_CHAT_URL, json=payload, headers=_headers())
            if response.status_code >= 500:
                raise VLMError(f"Server error {response.status_code}: {response.text[:300]}")
            if response.status_code >= 400:  # a bad request will not fix itself -> no retry
                raise ValueError(f"Request rejected ({response.status_code}): {response.text[:300]}")
            result = _parse(response.json())
            result["ms"] = round((time.perf_counter() - start) * 1000, 1)
            result["attempts"] = attempt
            if record_metric:
                record("vlm_ms", result["ms"])
            return result
        except ValueError:
            raise
        except httpx.TimeoutException as exc:
            last_error = exc
        except httpx.ConnectError as exc:
            last_error = ConnectionError(_not_running_message())
            time.sleep(min(0.5, max(0.0, deadline - time.perf_counter())))
        except (VLMError, httpx.HTTPError) as exc:
            last_error = exc
    if isinstance(last_error, ConnectionError):
        raise last_error
    if last_error is None or isinstance(last_error, httpx.TimeoutException):
        raise TimeoutError(f"llama-server did not answer within {timeout_s:.0f} s")
    raise VLMError(f"VLM failed after {max_retries + 1} attempts: {last_error}")


def ask_vlm(image_path: ImageLike, prompt: str, **kwargs) -> str:
    """Send image + prompt to the local VLM and return its raw text answer."""
    return ask_vlm_detailed(image_path, prompt, **kwargs)["text"]


# --------------------------------------------------------------------------- async API
async def ask_vlm_async(image_path: ImageLike, prompt: str, max_tokens: int = 256,
                        temperature: float = 0.1, system: Optional[str] = None,
                        timeout_s: Optional[float] = None, max_retries: Optional[int] = None) -> str:
    """`await ask_vlm_async(path, prompt)` - for code that already uses asyncio."""
    timeout_s = config.VLM_TIMEOUT_S if timeout_s is None else timeout_s
    max_retries = config.VLM_MAX_RETRIES if max_retries is None else max_retries
    payload = build_payload(image_path, prompt, max_tokens, temperature, system)
    start = time.perf_counter()
    last_error: Optional[BaseException] = None
    try:
        async with asyncio.timeout(timeout_s) if hasattr(asyncio, "timeout") else _null():
            async with httpx.AsyncClient(timeout=timeout_s) as client:
                for attempt in range(1, max_retries + 2):
                    try:
                        response = await client.post(_CHAT_URL, json=payload, headers=_headers())
                        if response.status_code >= 400 and response.status_code < 500:
                            raise ValueError(f"Request rejected ({response.status_code}): {response.text[:300]}")
                        response.raise_for_status()
                        text = _parse(response.json())["text"]
                        record("vlm_ms", (time.perf_counter() - start) * 1000)
                        return text
                    except ValueError:
                        raise
                    except httpx.ConnectError:
                        last_error = ConnectionError(_not_running_message())
                        await asyncio.sleep(0.5)
                    except (VLMError, httpx.HTTPError) as exc:
                        last_error = exc
    except (asyncio.TimeoutError, TimeoutError):
        raise TimeoutError(f"llama-server did not answer within {timeout_s:.0f} s")
    if isinstance(last_error, ConnectionError):
        raise last_error
    raise VLMError(f"VLM failed after {max_retries + 1} attempts: {last_error}")


class _null:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


# --------------------------------------------------------------------------- server checks
def server_is_up(url: Optional[str] = None) -> bool:
    """True when llama-server is running AND the model has finished loading."""
    base = (url or config.LLAMA_SERVER_URL).rstrip("/")
    try:
        r = httpx.get(f"{base}/health", timeout=2, headers=_headers())
        if r.status_code == 404:  # Ollama (the Plan-B runtime) has no /health
            r = httpx.get(f"{base}/v1/models", timeout=2, headers=_headers())
        return r.status_code == 200
    except httpx.HTTPError:
        return False


def wait_for_server(timeout_s: float = 120, url: Optional[str] = None) -> bool:
    end = time.time() + timeout_s
    while time.time() < end:
        if server_is_up(url):
            return True
        time.sleep(1)
    return False


if __name__ == "__main__":  # quick manual test: python -m models.vlm_client picture.png "question"
    import sys

    if len(sys.argv) < 2:
        print('Usage: python -m models.vlm_client <image> ["prompt"]')
        raise SystemExit(1)
    question = sys.argv[2] if len(sys.argv) > 2 else "Describe this page in one sentence."
    out = ask_vlm_detailed(sys.argv[1], question)
    print(out["text"])
    print(f"\n[{out['ms']:.0f} ms, {out['prompt_tokens']} prompt tokens, {out['completion_tokens']} answer tokens]")
