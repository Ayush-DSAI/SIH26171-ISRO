# INTEGRATION.md - how the team uses Shaurya's module

Everything lives in the `models/` folder (copy it into the repo root) and talks to
**llama-server on http://127.0.0.1:8081** (Shaurya's laptop).

## 1. Local VLM - `models/vlm_client.py`  (for Ayush + Aditi)

```python
from models.vlm_client import ask_vlm, ask_vlm_async, ask_vlm_detailed

text = ask_vlm("screenshots/before.png", "Where is the Login button? ...")     # -> str
text = await ask_vlm_async(png_bytes, "Describe this page in one sentence.")   # async Playwright code
info = ask_vlm_detailed("before.png", "...")   # {'text', 'ms', 'prompt_tokens', 'completion_tokens', ...}
```
* `image_path` can be a file path, raw PNG bytes (`page.screenshot()`), or a PIL image.
* Raises `TimeoutError` if no answer in 10 s, `ConnectionError` if the server is not running.
* Retries up to 2 times on empty answers / server errors. Records `vlm_ms` automatically.
* **Coordinates (for Aditi):** Qwen3.5 usually answers boxes on a **0-1000 scale**
  (`pixel_x = value / 1000 * image_width`). The smoke test prints which style your server uses.

## 2. Remote model - `models/remote_client.py`  (for Ayush + Himanshu)

```python
from models import remote_client
text = remote_client.ask_remote(result["sanitized_image_path"], task)   # -> str
if remote_client.last_call["mocked"]:
    label = "MOCKED - Remote Model"
else:
    label = "Remote Model Response (sanitized data only)"
```
* Refuses any file whose name does not contain `sanitized` (raises `NotSanitizedError`).
* Masks e-mails / phone / Aadhaar / PAN / card numbers inside the task text.
* No API key in `.env` -> returns the mock answer `"Based on the interface, click the Login button."`

## 3. Verification - `models/verification.py`  (for Ayush)

```python
from models.verification import verify_action
check = verify_action("before.png", "after.png", target_bbox=[342, 280, 120, 40])
# {'changed': True, 'changed_fraction': 0.18, 'ssim': 0.71, 'changed_bbox': [...], 'target_changed': True, 'ms': 30}
if not check["changed"]:
    ...retry with a more specific prompt (max 2 retries)
```

## 4. Metrics - `models/metrics.py`  (for Ayush + Himanshu)

```python
from models.metrics import timer, get_metrics, metrics_router
with timer("redaction_ms"):
    result = redact(image_path, dom_json)
app.include_router(metrics_router)      # GET /metrics -> {"vlm_ms", "redaction_ms", "vram_mb", ...}
```
Agree with Himanshu on ONE /metrics endpoint (his telemetry can call `get_metrics()`).

## 5. VRAM - `models/vram_monitor.py`

```python
from models.vram_monitor import get_vram_mb
get_vram_mb()   # {'used_mb': 4210, 'total_mb': 8188, 'gpu_util_pct': 35.0, ...}
```

## Settings

All settings are in `.env` (never commit it). Teammates on another laptop change only
`LLAMA_SERVER_URL=http://<Shaurya's IP>:8081` and `LLAMA_API_KEY=<the shared key>`.
