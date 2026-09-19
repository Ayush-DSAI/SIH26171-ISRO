"""LATENCY REPORT (Day 8-9, PPT evidence #7).

Reads results/metrics_log.jsonl (every timing recorded by ask_vlm, ask_remote and
the team's `with timer("..."):` blocks) and prints the table for the PPT:
  stage | count | min | avg | max | p95
Run after the team has run the full pipeline a few times.
"""
from __future__ import annotations

import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import banner, fail, ok, pause_if_double_clicked  # noqa: E402

from models import config  # noqa: E402

NICE = {"vlm_ms": "Local VLM inference", "grounding_ms": "Grounding", "redaction_ms": "PII detection + redaction",
        "remote_ms": "Remote reasoning", "screenshot_ms": "Screenshot capture", "action_ms": "Action execution",
        "verification_ms": "Verification", "total_ms": "Total per step"}


def main() -> int:
    banner("LATENCY REPORT")
    log = config.RESULTS_DIR / "metrics_log.jsonl"
    if not log.exists():
        fail("No results/metrics_log.jsonl yet - run the pipeline (or the smoke test) first.")
        return 1
    values: dict[str, list[float]] = {}
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
            values.setdefault(item["name"], []).append(float(item["ms"]))
        except (ValueError, KeyError):
            continue
    L = [f"# Latency report - {datetime.now():%Y-%m-%d %H:%M}", "",
         "| Stage | Runs | Min ms | Avg ms | Max ms | P95 ms |", "|---|---|---|---|---|---|"]
    for name, v in sorted(values.items(), key=lambda kv: list(NICE).index(kv[0]) if kv[0] in NICE else 99):
        s = sorted(v)
        p95 = s[min(len(s) - 1, int(round(0.95 * (len(s) - 1))))]
        L.append(f"| {NICE.get(name, name)} | {len(s)} | {s[0]:.0f} | {statistics.mean(s):.0f} | {s[-1]:.0f} | {p95:.0f} |")
    out = config.RESULTS_DIR / "latency_report.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[2:]))
    ok(f"Saved {out}")
    return 0


if __name__ == "__main__":
    code = main()
    pause_if_double_clicked()
    sys.exit(code)
