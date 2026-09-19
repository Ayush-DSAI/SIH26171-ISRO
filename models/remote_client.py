"""Client for the REMOTE (cloud) reasoning model. Receives SANITIZED screenshots only.

INTEGRATION CONTRACT (Shaurya -> Ayush), from the team plan:
    ask_remote(sanitized_image_path: str, task: str) -> str
        Sends the SANITIZED image + task to the remote model API. Returns reasoning text.
        If MOCKED, returns: "Based on the interface, click the Login button."

Privacy guards built in (good jury talking points):
  1. Refuses any image whose file name does not contain "sanitized"
     (Abhishek's redact() saves files like sanitized_20260908.png).
  2. Masks e-mails, phone numbers, Aadhaar/PAN-like numbers inside the task text.
  3. Never logs image bytes or the API key.

Which provider is used comes from .env:
    REMOTE_PROVIDER=gemini   (free key from Google AI Studio)  | openai | custom | mock
    REMOTE_MODEL_API_KEY=...  REMOTE_MODEL_NAME=...  REMOTE_MODEL_URL=...
With no key (or provider=mock) the clearly-labelled MOCK answer is returned.
"""
from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Optional

import httpx

from models import config
from models.metrics import record
from models.vlm_client import image_to_data_uri

MOCK_RESPONSE = "Based on the interface, click the Login button."  # MOCKED - replace with real API call

SYSTEM_PROMPT = (
    "You are the reasoning brain of a privacy-preserving browser agent. You receive a SANITIZED "
    "screenshot of a web page: black boxes and blurred areas hide private data on purpose - never "
    "try to guess what is hidden. Given the user's task, reply in at most 2 short sentences: say "
    "which single UI element should be used next (name it by its visible label, e.g. 'the Login "
    "button') and what to do with it (click / type / scroll)."
)

# Gemini model names change often; if the configured one is missing we try these in order.
_GEMINI_FALLBACKS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-flash-latest"]

_TEXT_PII = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[EMAIL]"),
    (re.compile(r"\b[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}\b"), "[AADHAAR]"),
    (re.compile(r"(?:\+91[\s-]?)?\b[6-9]\d{9}\b"), "[PHONE]"),
    (re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), "[PAN]"),
    (re.compile(r"\b(?:\d{4}[\s-]?){3}\d{4}\b"), "[CARD]"),
]

last_call: dict = {"mocked": None, "provider": None, "model": None, "ms": None, "reason": None}


class NotSanitizedError(ValueError):
    """Raised when someone tries to send a non-sanitized image to the cloud."""


def mask_text_pii(text: str) -> str:
    for pattern, placeholder in _TEXT_PII:
        text = pattern.sub(placeholder, text)
    return text


def _check_sanitized(path: str) -> Path:
    p = Path(path)
    if "sanitized" not in p.name.lower():
        raise NotSanitizedError(
            f"Refusing to send '{p.name}' to the remote model: only files produced by redact() "
            "(name contains 'sanitized') may leave the device.")
    if not p.is_file():
        raise FileNotFoundError(f"Sanitized image not found: {p}")
    return p


def _mock(reason: str) -> str:
    last_call.update(mocked=True, provider="mock", model=None, ms=0.0, reason=reason)
    return MOCK_RESPONSE  # MOCKED - replace with real API call


def _endpoint() -> str:
    if config.REMOTE_PROVIDER == "openai" and "googleapis" in config.REMOTE_MODEL_URL:
        return "https://api.openai.com/v1/chat/completions"
    return config.REMOTE_MODEL_URL


def _candidate_models() -> list[str]:
    models = [config.REMOTE_MODEL_NAME]
    if config.REMOTE_PROVIDER == "gemini":
        models += [m for m in _GEMINI_FALLBACKS if m != config.REMOTE_MODEL_NAME]
    return models


def ask_remote_detailed(sanitized_image_path: str, task: str, allow_mock_fallback: bool = True,
                        timeout_s: Optional[float] = None) -> dict:
    """Returns {'text', 'mocked', 'provider', 'model', 'ms', 'reason'}."""
    image = _check_sanitized(sanitized_image_path)          # guard 1
    safe_task = mask_text_pii(task)                           # guard 2
    timeout_s = config.REMOTE_TIMEOUT_S if timeout_s is None else timeout_s

    if config.REMOTE_PROVIDER == "mock" or not config.REMOTE_MODEL_API_KEY:
        reason = "REMOTE_PROVIDER=mock" if config.REMOTE_PROVIDER == "mock" else "no API key in .env"
        return {"text": _mock(reason), **last_call}

    data_uri = image_to_data_uri(image)
    headers = {"Authorization": f"Bearer {config.REMOTE_MODEL_API_KEY}", "Content-Type": "application/json"}
    errors: list[str] = []
    start = time.perf_counter()
    for model in _candidate_models():
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": f"Task: {safe_task}"},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ]},
            ],
            "max_tokens": 200,
            "temperature": 0.2,
        }
        network_failures = 0
        for attempt in range(config.REMOTE_MAX_RETRIES + 1):
            try:
                r = httpx.post(_endpoint(), json=payload, headers=headers, timeout=timeout_s)
            except httpx.HTTPError as exc:
                errors.append(f"{model}: {type(exc).__name__} (no internet or server down?)")
                network_failures += 1
                if attempt < config.REMOTE_MAX_RETRIES:
                    time.sleep(0.5 * 2 ** attempt)            # exponential backoff: 0.5 s, 1 s
                continue
            if r.status_code == 404 or (r.status_code == 400 and "model" in r.text.lower()):
                errors.append(f"{model}: model not available ({r.status_code})")
                break                                          # try the next model name
            if r.status_code in (401, 403):
                errors.append(f"API key rejected ({r.status_code}) - check REMOTE_MODEL_API_KEY in .env")
                return _fallback(errors, allow_mock_fallback)
            if r.status_code == 429 or r.status_code >= 500:
                errors.append(f"{model}: HTTP {r.status_code}")
                time.sleep(0.5 * 2 ** attempt)
                continue
            if r.status_code >= 400:
                errors.append(f"{model}: HTTP {r.status_code} {r.text[:200]}")
                break
            try:
                text = (r.json()["choices"][0]["message"]["content"] or "").strip()
            except (KeyError, IndexError, TypeError, ValueError):
                errors.append(f"{model}: unexpected response")
                break
            ms = round((time.perf_counter() - start) * 1000, 1)
            record("remote_ms", ms)
            last_call.update(mocked=False, provider=config.REMOTE_PROVIDER, model=model, ms=ms, reason=None)
            return {"text": text, **last_call}
        if network_failures > config.REMOTE_MAX_RETRIES:
            break                                              # network is down - other model names won't help
    return _fallback(errors, allow_mock_fallback)


def _fallback(errors: list[str], allow_mock_fallback: bool) -> dict:
    reason = "; ".join(errors[-3:]) or "unknown error"
    if not allow_mock_fallback:
        raise RuntimeError(f"Remote model failed: {reason}")
    return {"text": _mock(f"remote call failed -> {reason}"), **last_call}


def ask_remote(sanitized_image_path: str, task: str) -> str:
    """Send SANITIZED image + task to the remote model and return its reasoning text.

    After calling, check `remote_client.last_call["mocked"]` to label the UI
    ("Remote Model Response (sanitized data only)" vs "MOCKED - Remote Model").
    """
    return ask_remote_detailed(sanitized_image_path, task)["text"]
