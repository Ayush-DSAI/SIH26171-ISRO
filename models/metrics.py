"""Timing + VRAM metrics for the whole pipeline (Day 6 task: GET /metrics).

How teammates use it:
    from models.metrics import timer, record, get_metrics
    with timer("redaction_ms"):
        result = redact(image_path, dom_json)      # Abhishek's function
    print(get_metrics())   # {'vlm_ms': 412.3, 'redaction_ms': 45.1, 'vram_mb': 4213, ...}

ask_vlm() records "vlm_ms" automatically, ask_remote() records "remote_ms".
Every value is also appended to results/metrics_log.jsonl so you can make
the latency table for the PPT later (scripts/latency_report.py).

Add the endpoint to the FastAPI app (Ayush / Himanshu, one line):
    from models.metrics import metrics_router
    app.include_router(metrics_router)        # -> GET /metrics
"""
from __future__ import annotations

import json
import statistics
import threading
import time
from contextlib import contextmanager
from typing import Optional

from models.config import RESULTS_DIR
from models.vram_monitor import used_mb

LOG_FILE = RESULTS_DIR / "metrics_log.jsonl"
_lock = threading.Lock()
_last: dict[str, float] = {}
_history: dict[str, list[float]] = {}


def record(name: str, ms: float, run_id: Optional[str] = None) -> None:
    """Store one timing (milliseconds). Never pass personal data in `name`."""
    ms = round(float(ms), 1)
    with _lock:
        _last[name] = ms
        _history.setdefault(name, []).append(ms)
        try:
            with LOG_FILE.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"t": time.time(), "name": name, "ms": ms, "run_id": run_id}) + "\n")
        except OSError:
            pass  # logging must never crash the agent


@contextmanager
def timer(name: str, run_id: Optional[str] = None):
    start = time.perf_counter()
    try:
        yield
    finally:
        record(name, (time.perf_counter() - start) * 1000, run_id)


def _summary(values: list[float]) -> dict:
    ordered = sorted(values)
    p95 = ordered[min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))]
    return {"count": len(values), "min": ordered[0], "avg": round(statistics.mean(values), 1),
            "max": ordered[-1], "p95": p95}


def get_metrics() -> dict:
    """What GET /metrics returns: last values + averages + current VRAM."""
    with _lock:
        last = dict(_last)
        summary = {k: _summary(v) for k, v in _history.items() if v}
    return {
        "vlm_ms": last.get("vlm_ms"),
        "redaction_ms": last.get("redaction_ms"),
        "vram_mb": used_mb(),
        "last": last,
        "summary": summary,
    }


def reset() -> None:
    with _lock:
        _last.clear()
        _history.clear()


try:  # FastAPI is optional - only needed inside the team's server
    from fastapi import APIRouter

    metrics_router = APIRouter()

    @metrics_router.get("/metrics")
    def metrics_endpoint() -> dict:
        return get_metrics()
except ImportError:  # pragma: no cover
    metrics_router = None
