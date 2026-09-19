"""MINI-PROJECT B - VLM benchmark (latency x quantization x resolution + VRAM x context size).

Fully automatic. For every quantization (default Q4_K_M and Q5_K_M) it:
  starts its own llama-server -> measures load time + VRAM -> sends every test
  screenshot at 720p and 1080p -> records time, tokens, VRAM peak, the answer,
  and (for synthetic pages) whether the Login-button box was correct -> stops the server.
Then it tests VRAM at context sizes 2048 / 4096 / 8192.

Outputs (for the PPT and your mini-project README):
  results/benchmark_raw.csv       every single request
  results/benchmark_summary.csv   one line per quantization x resolution
  results/benchmark_report.md     the finished report (tables + notes)

Close the normal VLM server window before running this (so measurements are clean).
Run:  .venv\\Scripts\\python.exe scripts\\benchmark_model.py
      .venv\\Scripts\\python.exe scripts\\benchmark_model.py --quants Q4_K_M --res 720p   (quick)
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (DESCRIBE_PROMPT, GROUNDING_PROMPT, ROOT, TempServer, ask_raw, banner,  # noqa: E402
                     center_inside, fail, interpret_box, ok, parse_four_numbers,
                     pause_if_double_clicked, warn)

from models import config  # noqa: E402
from models.vlm_client import server_is_up  # noqa: E402
from models.vram_monitor import VramPoller, get_vram_mb, used_mb  # noqa: E402

RESULTS = config.RESULTS_DIR


def stats(values: list[float]) -> dict:
    if not values:
        return {"min": None, "avg": None, "max": None, "p95": None}
    v = sorted(values)
    return {"min": round(v[0]), "avg": round(statistics.mean(v)), "max": round(v[-1]),
            "p95": round(v[min(len(v) - 1, int(round(0.95 * (len(v) - 1))))])}


def list_images(res: str, limit: int) -> list[Path]:
    folder = ROOT / "test_images" / res
    images = sorted(folder.glob("synth_*.png")) + sorted(folder.glob("web_*.png"))
    extra = sorted(p for p in folder.glob("*.png") if not p.name.startswith(("synth_", "web_")))
    return (images + extra)[:limit]


def run_quant(quant: str, resolutions: list[str], n_images: int, truth: dict, rows: list, port: int) -> dict:
    model = ROOT / "weights" / f"Qwen3.5-4B-{quant}.gguf"
    if not model.exists():
        from download_model import download
        print(f"  {model.name} is missing - downloading it now (about {3 if quant != 'Q4_K_M' else 2.7} GB)...")
        download(quant)
    info: dict = {"quant": quant, "file_gb": round(model.stat().st_size / 1e9, 2)}
    baseline = used_mb()
    print(f"\n  Starting llama-server with {model.name} ...")
    with TempServer(str(model), port=port, ctx=config.CTX_SIZE, log_name=f"llama_server_{quant}.log") as srv:
        time.sleep(2)
        info.update(load_s=srv.load_seconds, vram_baseline_mb=baseline, vram_loaded_mb=used_mb(),
                    memory_lines=srv.memory_lines())
        ok(f"loaded in {srv.load_seconds}s, VRAM {baseline} -> {info['vram_loaded_mb']} MB")
        warm = list_images(resolutions[0], 1)
        if warm:
            ask_raw(srv.url, warm[0], DESCRIBE_PROMPT, max_tokens=20)  # warm-up, not counted
        for res in resolutions:
            images = list_images(res, n_images)
            if not images:
                warn(f"no images in test_images/{res} - run make_test_images.py first")
                continue
            print(f"  {quant} @ {res}: {len(images)} screenshots", end="", flush=True)
            for img in images:
                key = f"{res}/{img.name}"
                gt = truth.get(key)
                prompt = GROUNDING_PROMPT.format(target=gt["target"]) if gt else DESCRIBE_PROMPT
                row = {"quant": quant, "resolution": res, "image": img.name,
                       "task": "grounding" if gt else "describe"}
                try:
                    with VramPoller(0.05) as poll:
                        out = ask_raw(srv.url, img, prompt, max_tokens=64 if gt else 60)
                    row.update(total_ms=out["ms"], prompt_ms=out["prompt_ms"], predicted_ms=out["predicted_ms"],
                               prompt_tokens=out["prompt_tokens"], answer_tokens=out["completion_tokens"],
                               vram_peak_mb=poll.peak_mb, answer=out["text"].replace("\n", " ")[:300], error="")
                    if gt:
                        nums = parse_four_numbers(out["text"])
                        boxes = interpret_box(nums, gt["width"], gt["height"]) if nums else {}
                        row["hit_pixel"] = int(bool(boxes) and center_inside(boxes["pixel_xyxy"], gt["bbox"]))
                        row["hit_norm1000"] = int(bool(boxes) and center_inside(boxes["norm1000_xyxy"], gt["bbox"]))
                    print(".", end="", flush=True)
                except Exception as exc:  # noqa: BLE001
                    row.update(error=str(exc)[:200])
                    print("x", end="", flush=True)
                rows.append(row)
            print()
    return info


def ctx_test(ctx_sizes: list[int], port: int) -> list[dict]:
    model = ROOT / "weights" / "Qwen3.5-4B-Q4_K_M.gguf"
    img720 = list_images("720p", 1)
    img1080 = list_images("1080p", 1)
    out = []
    for ctx in ctx_sizes:
        entry = {"ctx": ctx}
        try:
            with TempServer(str(model), port=port, ctx=ctx, log_name=f"llama_server_ctx{ctx}.log"):
                time.sleep(2)
                entry["vram_loaded_mb"] = used_mb()
                for label, imgs in (("720p", img720), ("1080p", img1080)):
                    if not imgs:
                        continue
                    try:
                        with VramPoller(0.05) as poll:
                            r = ask_raw(f"http://127.0.0.1:{port}", imgs[0], DESCRIBE_PROMPT, max_tokens=40)
                        entry[f"{label}_ok"] = True
                        entry[f"{label}_prompt_tokens"] = r["prompt_tokens"]
                        entry[f"{label}_peak_mb"] = poll.peak_mb
                    except Exception as exc:  # noqa: BLE001
                        entry[f"{label}_ok"] = False
                        entry[f"{label}_error"] = str(exc)[:150]
            ok(f"ctx {ctx}: loaded VRAM {entry.get('vram_loaded_mb')} MB, "
               f"720p {'fits' if entry.get('720p_ok') else 'FAILS'}, 1080p {'fits' if entry.get('1080p_ok') else 'FAILS'}")
        except Exception as exc:  # noqa: BLE001
            entry["error"] = str(exc)[:200]
            fail(f"ctx {ctx}: {exc}")
        out.append(entry)
    return out


def write_outputs(rows: list, infos: list, ctx_rows: list, gpu: dict | None) -> Path:
    fields = ["quant", "resolution", "image", "task", "total_ms", "prompt_ms", "predicted_ms", "prompt_tokens",
              "answer_tokens", "vram_peak_mb", "hit_pixel", "hit_norm1000", "answer", "error"]
    with (RESULTS / "benchmark_raw.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    summary = []
    for info in infos:
        seen = [r["resolution"] for r in rows if r["quant"] == info["quant"]]
        for res in dict.fromkeys(seen):  # keeps the order 720p, 1080p
            sel = [r for r in rows if r["quant"] == info["quant"] and r["resolution"] == res and not r["error"]]
            errs = sum(1 for r in rows if r["quant"] == info["quant"] and r["resolution"] == res and r["error"])
            g = [r for r in sel if r["task"] == "grounding"]
            s = stats([r["total_ms"] for r in sel])
            summary.append({
                "quant": info["quant"], "resolution": res, "images": len(sel), "errors": errs,
                "min_ms": s["min"], "avg_ms": s["avg"], "max_ms": s["max"], "p95_ms": s["p95"],
                "avg_prompt_tokens": round(statistics.mean([r["prompt_tokens"] or 0 for r in sel])) if sel else None,
                "avg_read_image_ms": round(statistics.mean([r["prompt_ms"] or 0 for r in sel])) if sel else None,
                "avg_write_answer_ms": round(statistics.mean([r["predicted_ms"] or 0 for r in sel])) if sel else None,
                "vram_peak_mb": max((r["vram_peak_mb"] or 0 for r in sel), default=None),
                "grounding_hits_norm1000": f"{sum(r.get('hit_norm1000', 0) for r in g)}/{len(g)}" if g else "-",
                "grounding_hits_pixel": f"{sum(r.get('hit_pixel', 0) for r in g)}/{len(g)}" if g else "-",
            })
    with (RESULTS / "benchmark_summary.csv").open("w", newline="", encoding="utf-8") as f:
        if summary:
            w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
            w.writeheader()
            w.writerows(summary)

    L = [f"# VLM Benchmark Report - Qwen3.5-4B on {gpu['name'] if gpu else 'GPU'}",
         "", f"Generated {datetime.now():%Y-%m-%d %H:%M}. Runtime: llama.cpp llama-server "
         f"(context {config.CTX_SIZE}, all layers on GPU, 1 slot, prompt cache off so every image is measured cold).",
         "", "## 1. Latency per quantization and resolution", "",
         "| Quant | File size | Resolution | Images | Min ms | Avg ms | Max ms | P95 ms | Read image ms | Write answer ms | Image tokens | VRAM peak | Grounding hits (0-1000 scale) | Grounding hits (pixels) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    sizes = {i["quant"]: i["file_gb"] for i in infos}
    for s in summary:
        L.append(f"| {s['quant']} | {sizes[s['quant']]} GB | {s['resolution']} | {s['images']} | {s['min_ms']} | "
                 f"{s['avg_ms']} | {s['max_ms']} | {s['p95_ms']} | {s['avg_read_image_ms']} | {s['avg_write_answer_ms']} | "
                 f"{s['avg_prompt_tokens']} | {s['vram_peak_mb']} MB | "
                 f"{s['grounding_hits_norm1000']} | {s['grounding_hits_pixel']} |")
    L += ["", "Grounding hits = on synthetic login pages with a known button position, the centre of the model's box "
          "landed on the button. The higher of the two columns shows which coordinate style the model uses.",
          "Read image ms / Write answer ms come from llama-server's own timings (prompt processing vs generation).",
          "", "## 2. Load time and memory per quantization", "",
          "| Quant | Load time | VRAM before | VRAM after load |", "|---|---|---|---|"]
    for i in infos:
        L.append(f"| {i['quant']} | {i['load_s']} s | {i['vram_baseline_mb']} MB | {i['vram_loaded_mb']} MB |")
    L += ["", "## 3. VRAM vs context size (Q4_K_M)", "",
          "| Context | VRAM after load | 720p works? (tokens) | 1080p works? (tokens) |", "|---|---|---|---|"]
    for c in ctx_rows:
        def cell(res: str) -> str:
            if c.get(f"{res}_ok"):
                return f"yes ({c.get(f'{res}_prompt_tokens')})"
            return "NO - too many tokens" if f"{res}_error" in c else "-"
        L.append(f"| {c['ctx']} | {c.get('vram_loaded_mb', 'error')} MB | {cell('720p')} | {cell('1080p')} |")
    L += ["", "## 4. llama-server's own memory report (Q4_K_M)", "", "```"]
    L += (infos[0]["memory_lines"] if infos else []) or ["(not found in log)"]
    L += ["```", "", "## 5. Notes to fill in by hand", "",
          "- Output quality: open benchmark_raw.csv, read the `answer` column for the web_* screenshots, "
          "and write 2 lines on whether Q5_K_M described pages better than Q4_K_M.",
          "- Decision: which quantization do we keep, and why (speed vs quality vs VRAM)?", ""]
    path = RESULTS / "benchmark_report.md"
    path.write_text("\n".join(L), encoding="utf-8")
    (RESULTS / "benchmark_meta.json").write_text(json.dumps({"infos": infos, "ctx": ctx_rows}, indent=2))
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quants", nargs="+", default=["Q4_K_M", "Q5_K_M"])
    ap.add_argument("--res", nargs="+", default=["720p", "1080p"])
    ap.add_argument("--images", type=int, default=20, help="screenshots per resolution")
    ap.add_argument("--ctx-test", nargs="*", type=int, default=[2048, 4096, 8192])
    ap.add_argument("--port", type=int, default=8099)
    args = ap.parse_args()

    banner("MINI-PROJECT B - VLM BENCHMARK")
    if server_is_up():
        warn("Your normal VLM server window is still open. Close it (click it, press Ctrl+C) for clean VRAM numbers.")
        input("  Press Enter when it is closed (or just Enter to continue anyway)...")
    truth_file = ROOT / "test_images" / "ground_truth.json"
    if not truth_file.exists() or not list_images("720p", 1):
        from make_test_images import make_real, make_synthetic
        make_synthetic()
        make_real()
    truth = json.loads(truth_file.read_text())
    gpu = get_vram_mb()
    rows: list = []
    infos = []
    t0 = time.time()
    for quant in args.quants:
        try:
            infos.append(run_quant(quant, args.res, args.images, truth, rows, args.port))
        except Exception as exc:  # noqa: BLE001
            fail(f"{quant}: {exc}")
    ctx_rows = ctx_test(args.ctx_test, args.port) if args.ctx_test else []
    if not infos:
        fail("Nothing was measured.")
        return 1
    report = write_outputs(rows, infos, ctx_rows, gpu)
    banner(f"BENCHMARK DONE in {time.time() - t0:.0f}s")
    print((report).read_text(encoding="utf-8").split("## 2.")[0])
    ok(f"Full report: {report}")
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception as exc:  # noqa: BLE001
        fail(f"{type(exc).__name__}: {exc}")
        code = 1
    pause_if_double_clicked()
    sys.exit(code)
