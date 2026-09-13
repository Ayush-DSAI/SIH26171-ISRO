import asyncio
import json
import secrets
import sys
import time
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agent.loop import run_agent_step


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class TaskRequest(BaseModel):
    task: str
    url: str


class TaskInfo:
    def __init__(self, run_id: str, task: str, url: str):
        self.run_id = run_id
        self.task = task
        self.url = url
        self.status: str = "queued"
        self.before_image: Optional[str] = None
        self.after_image: Optional[str] = None
        self.sanitized_image_path: Optional[str] = None
        self.grounding: Optional[dict] = None
        self.execution: Optional[dict] = None
        self.redaction: Optional[dict] = None
        self.remote_response: Optional[str] = None


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="Browser Agent API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = PROJECT_ROOT / "frontend"
TMP_DIR = PROJECT_ROOT / "tmp"
FRONTEND_DIR.mkdir(exist_ok=True)
TMP_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
app.mount("/tmp",    StaticFiles(directory=str(TMP_DIR)),      name="tmp")


# ---------------------------------------------------------------------------
# WebSocket broadcast infrastructure
# ---------------------------------------------------------------------------

_active_sockets: set[WebSocket] = set()
_current_task: Optional[TaskInfo] = None


async def broadcast(event: dict) -> None:
    if not _active_sockets:
        return
    payload = json.dumps(event, default=str)
    dead = set()
    for ws in _active_sockets:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.add(ws)
    _active_sockets.difference_update(dead)


# ---------------------------------------------------------------------------
# HTTP endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "service": "browser-agent-api",
        "endpoints": {
            "POST /task":              "Submit {task, url} -> {run_id, status}",
            "WS   /status":           "Stream of JSON progress events",
            "GET  /metrics":          "Current VLM / redaction latency and VRAM stats",
            "GET  /static/index.html": "Dashboard UI",
        },
    }


@app.get("/metrics")
async def get_metrics():
    """
    Returns mocked real-time performance metrics.

    Day 8 plan: replace with live readings from:
      - torch.cuda.memory_allocated() → vram_mb
      - instrumented timers around VLM inference → vlm_ms
      - instrumented timers around mock_redact()  → redaction_ms
    """
    return {
        "vlm_ms":       420,
        "redaction_ms": 45,
        "vram_mb":      3800,
    }


@app.websocket("/status")
async def status_stream(websocket: WebSocket):
    await websocket.accept()
    _active_sockets.add(websocket)
    try:
        if _current_task is not None:
            await websocket.send_json(
                {
                    "step":    "reconnect",
                    "status":  "info",
                    "run_id":  _current_task.run_id,
                    "task":    _current_task.task,
                    "state":   _current_task.status,
                }
            )
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    finally:
        _active_sockets.discard(websocket)


@app.post("/task")
async def submit_task(req: TaskRequest):
    global _current_task
    run_id = secrets.token_urlsafe(6)
    info = TaskInfo(run_id=run_id, task=req.task, url=req.url)
    _current_task = info
    task_obj = asyncio.create_task(_run_agent(info))
    task_obj.add_done_callback(lambda fut: None if fut.cancelled() else fut.exception())
    return {"run_id": run_id, "status": "queued"}


# ---------------------------------------------------------------------------
# Agent runner
# ---------------------------------------------------------------------------

def _ts_ms() -> int:
    return int(time.perf_counter() * 1000)


async def _run_agent(info: TaskInfo) -> None:
    t0 = _ts_ms()
    await broadcast(
        {
            "step":   "init",
            "status": "start",
            "run_id": info.run_id,
            "task":   info.task,
            "url":    info.url,
            "ms":     0,
        }
    )

    try:
        info.status = "launching"

        def _run_playwright_in_process(task: str, url: str) -> dict:
            import asyncio as _aio

            if sys.platform == "win32":
                _aio.set_event_loop_policy(_aio.WindowsProactorEventLoopPolicy())

            async def _pw_work() -> dict:
                from playwright.async_api import async_playwright as _pw

                async with _pw() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(
                        viewport={"width": 1280, "height": 720}
                    )
                    page = await context.new_page()

                    if url.startswith("file://"):
                        goto_url = url
                    else:
                        candidate = Path(url)
                        if candidate.exists():
                            goto_url = candidate.resolve().as_uri()
                        else:
                            goto_url = url

                    await page.goto(goto_url, wait_until="domcontentloaded")

                    result = await run_agent_step(
                        page, task=task, mock_grounding=True
                    )

                    await browser.close()
                    return result

            return _aio.run(_pw_work())

        from playwright.async_api import async_playwright  # noqa: F401

        result = await asyncio.to_thread(_run_playwright_in_process, info.task, info.url)

        info.before_image         = result["before_image"]
        info.after_image          = result["after_image"]
        info.grounding            = result["grounding"]
        info.execution            = result["execution"]
        info.redaction            = result["redaction"]
        info.sanitized_image_path = result["sanitized_image_path"]
        info.remote_response      = result.get("remote_response", "")

        # ── navigate ────────────────────────────────────────────────────────
        await broadcast(
            {
                "step":   "navigate",
                "status": "done",
                "run_id": info.run_id,
                "ms":     _ts_ms() - t0,
                "url":    info.url,
            }
        )

        before_rel   = Path(info.before_image).name
        after_rel    = Path(info.after_image).name
        san_rel      = Path(info.sanitized_image_path).name

        # ── before screenshot ────────────────────────────────────────────────
        await broadcast(
            {
                "step":   "screenshot",
                "status": "done",
                "run_id": info.run_id,
                "ms":     _ts_ms() - t0,
                "image":  f"/tmp/{before_rel}",
            }
        )

        # ── grounding ────────────────────────────────────────────────────────
        g = info.grounding or {}
        await broadcast(
            {
                "step":       "grounding",
                "status":     "done",
                "run_id":     info.run_id,
                "ms":         _ts_ms() - t0,
                "element":    g.get("element"),
                "bbox":       g.get("bbox"),
                "confidence": g.get("confidence"),
            }
        )

        # ── redaction ────────────────────────────────────────────────────────
        rd = info.redaction or {}
        pii_list  = rd.get("detected_pii", [])
        pii_count = len(pii_list)
        await broadcast(
            {
                "step":      "redaction",
                "status":    "done",
                "run_id":    info.run_id,
                "ms":        45,           # matches /metrics redaction_ms
                "pii_count": pii_count,
                "pii_types": [p["type"] for p in pii_list],
            }
        )

        # ── remote VLM ──────────────────────────────────────────────────────
        await broadcast(
            {
                "step":     "remote",
                "status":   "mocked",
                "run_id":   info.run_id,
                "ms":       1200,   # matches mocked VLM round-trip latency
                "response": info.remote_response,
            }
        )

        # ── action ───────────────────────────────────────────────────────────
        e = info.execution or {}
        await broadcast(
            {
                "step":   "action",
                "status": "done",
                "run_id": info.run_id,
                "ms":     _ts_ms() - t0,
                "action": e.get("action"),
                "target": e.get("target"),
            }
        )

        # ── after screenshot ─────────────────────────────────────────────────
        await broadcast(
            {
                "step":   "after_screenshot",
                "status": "done",
                "run_id": info.run_id,
                "ms":     _ts_ms() - t0,
                "image":  f"/tmp/{after_rel}",
            }
        )

        # ── complete ─────────────────────────────────────────────────────────
        info.status = "complete"
        await broadcast(
            {
                "step":                 "complete",
                "status":               "done",
                "run_id":               info.run_id,
                "ms":                   _ts_ms() - t0,
                "before_image":         f"/tmp/{before_rel}",
                "after_image":          f"/tmp/{after_rel}",
                "sanitized_image_path": f"/tmp/{san_rel}",
                "grounding":            info.grounding,
                "execution":            info.execution,
                "redaction":            info.redaction,
                "remote_response":      info.remote_response,
            }
        )
    except Exception as exc:
        info.status = "error"
        await broadcast(
            {
                "step":    "error",
                "status":  "error",
                "run_id":  info.run_id,
                "ms":      _ts_ms() - t0,
                "message": f"{type(exc).__name__}: {exc}",
            }
        )
