# PART 2 — REFERENCE ARCHITECTURE (All 17 Modules)

---

## A. Browser Interaction Layer

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Control a real browser: navigate, click, type, scroll, manage sessions |
| **Inputs** | Action commands from Agent Planner |
| **Outputs** | Page state changes, navigation events, error signals |
| **Technology** | **Playwright (Python)** |
| **Alternatives** | Selenium (slower, less modern), browser CDP directly (too low-level), Puppeteer (JS-only) |
| **Compute** | CPU only, negligible (~50 MB RAM for browser automation library) |
| **Runs** | Locally |
| **Why Playwright** | Async-first, built-in CDP access, auto-wait for elements, headless + headed modes, screenshot API, maintained by Microsoft, best Python browser automation library in 2026 |
| **Team must learn** | Playwright Python API, CDP basics, async/await patterns |

---

## B. Screen Capture / Observation

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Capture full-page or viewport screenshots for VLM input |
| **Inputs** | Current page reference from Playwright |
| **Outputs** | PNG/JPEG screenshot (1280×720 recommended for VRAM efficiency) |
| **Technology** | `page.screenshot()` via Playwright + optional `PIL`/`Pillow` for resize |
| **Alternatives** | CDP `Page.captureScreenshot` directly (more control over format/quality) |
| **Compute** | CPU, ~5–50ms per capture |
| **Runs** | Locally |
| **Why this fits** | Zero VRAM cost; screenshot resolution directly impacts VLM VRAM consumption. 720p is the sweet spot: readable text, manageable tokens |
| **Team must learn** | Image formats (PNG vs JPEG quality tradeoffs), resolution/aspect ratio management |

**Design decision:** Capture at 1280×720 for VLM input. Store full-resolution (1920×1080) for redaction visualization in demo.

---

## C. DOM Extraction

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Extract structured page information: elements, types, attributes, bounding boxes |
| **Inputs** | Live page reference |
| **Outputs** | JSON accessibility tree with bounding boxes + sensitive attribute flags |
| **Technology** | Playwright `page.accessibility.snapshot()` + custom CDP `DOM.getDocument` queries |
| **Alternatives** | BeautifulSoup on `page.content()` (loses bounding boxes), Playwright `locator.bounding_box()` per element (slow for many elements) |
| **Compute** | CPU, ~50–150ms for full page |
| **Runs** | Locally |
| **Why this fits** | DOM extraction is the **cheapest privacy signal**. `input[type=password]` is a guaranteed password field — no ML needed. |
| **Team must learn** | HTML structure, accessibility tree concepts, CDP protocol, DOM attributes for PII |

**Critical DOM attributes for PII detection:**
```python
SENSITIVE_SELECTORS = {
    'input[type="password"]': 'password',
    'input[type="email"]': 'email',
    'input[autocomplete="tel"]': 'phone',
    'input[autocomplete="cc-number"]': 'credit_card',
    'input[autocomplete="cc-csc"]': 'cvv',
    'input[name*="aadhaar"]': 'aadhaar',
    'input[name*="pan"]': 'pan_number',
    'input[name*="ssn"]': 'ssn',
    'input[id*="phone"]': 'phone',
    'input[id*="mobile"]': 'phone',
}
```

---

## D. Local VLM Inference

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Understand screenshots, describe UI, answer questions about the page |
| **Inputs** | Screenshot (720p PNG) + text prompt |
| **Outputs** | Text description, element identification, action suggestions |
| **Technology** | **Qwen3.5-4B-Instruct (GGUF Q4_K_M)** via **llama.cpp server** |
| **Alternatives** | SmolVLM 2.2B (smaller but weaker grounding), MiniCPM-V 2.6 (more capable but 6–8 GB), Moondream2 (very light but limited) |
| **Compute** | **~3.5 GB VRAM** (Q4_K_M), ~200–500ms inference |
| **Runs** | **Locally** — this is the core on-device component |
| **Why Qwen3.5-4B** | Best balance of size, grounding, UI understanding, and ecosystem (Qwen-Agent). At Q4, uses only 3.5 GB leaving 4.5 GB for everything else. Apache 2.0 licensed. |
| **Team must learn** | VLM basics, quantization concepts (GGUF, Q4/Q5/Q8), prompt engineering for grounding, llama.cpp server setup |

**VRAM Budget:**
```
Qwen3.5-4B Q4_K_M:        ~3,500 MB
KV Cache (2048 ctx):         ~400 MB
Vision encoder + projector:  ~300 MB
                           ─────────
Subtotal VLM:              ~4,200 MB
Remaining for other tasks: ~3,800 MB ✓
```

**Fallback models (if Qwen3.5-4B has issues):**
1. SmolVLM 2.2B — ultra-light, ~2 GB VRAM
2. Qwen2.5-VL-3B — slightly older but well-tested
3. MiniCPM-V 2.6 — more capable but tighter fit

---

## E. UI Grounding

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Map natural-language element descriptions to pixel coordinates |
| **Inputs** | Screenshot + element description ("the login button") |
| **Outputs** | Bounding box coordinates {x, y, width, height} or center point (x, y) |
| **Technology** | Same VLM (Qwen3.5-4B) with grounding-specific prompts + DOM bounding boxes as fallback |
| **Alternatives** | Dedicated grounding models (like GroundingDINO — but adds VRAM), DOM-only localization (misses visual elements) |
| **Compute** | Part of VLM inference — no additional VRAM |
| **Runs** | Locally |
| **Why this approach** | Using the same VLM for perception AND grounding avoids loading a second model. DOM bounding boxes provide high-precision fallback for standard HTML elements. |
| **Team must learn** | Coordinate systems (normalized vs pixel), bounding box formats, IoU (Intersection over Union) for accuracy measurement |

**Hybrid grounding strategy:**
```
IF element found in DOM with bounding box:
    → Use DOM coordinates (highest precision, zero cost)
ELIF VLM returns coordinates with high confidence:
    → Use VLM coordinates
ELSE:
    → Ask VLM to re-examine specific region
    → If still uncertain, report grounding failure
```

---

## F. OCR / Text Extraction

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Extract rendered text from screenshots for PII scanning |
| **Inputs** | Screenshot image (full or cropped region) |
| **Outputs** | List of {text, bounding_box, confidence} |
| **Technology** | **PaddleOCR (lightweight mode)** or VLM's built-in OCR capability |
| **Alternatives** | Tesseract (slower, less accurate on web content), EasyOCR (heavier), TrOCR (transformer-based, heavier) |
| **Compute** | ~200 MB VRAM for PaddleOCR lightweight; 0 additional if using VLM's OCR |
| **Runs** | Locally |
| **Why PaddleOCR** | Smallest accurate OCR engine, good on web screenshots, supports English + Indian languages, runs on GPU or CPU |
| **Team must learn** | OCR basics, text detection vs recognition, handling multi-language text |

**Key insight:** The VLM itself (Qwen3.5-4B) has decent OCR capability. For the MVP, we can use VLM-based OCR to avoid loading a separate model. PaddleOCR is the upgrade path for higher accuracy.

---

## G. PII Detection

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Identify personally identifiable information in DOM content and screenshot text |
| **Inputs** | DOM tree + OCR text output |
| **Outputs** | List of {pii_type, value, location, confidence, source} |
| **Technology** | **Multi-layer detection engine** (see below) |
| **Compute** | CPU-only for regex/DOM; ~50 MB for GLiNER edge model if used |
| **Runs** | Locally (MUST never send raw PII to remote) |
| **Why multi-layer** | No single technique catches everything. DOM catches tagged fields, regex catches patterns, NER catches unstructured text. |
| **Team must learn** | Regex patterns, Indian PII formats (Aadhaar Verhoeff checksum, PAN format), NER basics |

**Detection Layers:**
```
Layer 1: DOM Attributes (5ms, 100% precision for tagged fields)
├── input[type=password/email]
├── autocomplete attributes
└── name/id pattern matching

Layer 2: Regex on DOM Text Content (10ms)
├── Aadhaar: \b[2-9]\d{3}\s?\d{4}\s?\d{4}\b + Verhoeff
├── PAN: [A-Z]{5}[0-9]{4}[A-Z]
├── Email: standard email regex
├── Phone: \+?91[\s-]?\d{10} patterns
├── Credit card: Luhn-validated 16-digit
└── Context keywords near matches

Layer 3: OCR + Regex on Screenshot (50ms)
├── Run OCR on rendered page regions
└── Apply same regex patterns to OCR text

Layer 4 (stretch): GLiNER NER (100ms, optional)
├── Zero-shot NER for names, addresses
└── Only if VRAM budget allows
```

---

## H. Face Detection

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Detect human faces in screenshots for privacy masking |
| **Inputs** | Screenshot image |
| **Outputs** | List of face bounding boxes + confidence scores |
| **Technology** | **MediaPipe Face Detection (BlazeFace)** |
| **Alternatives** | UltraLight ONNX (~1 MB, less accurate), OpenCV Haar Cascades (outdated, many false positives), YOLO-Face (heavier) |
| **Compute** | **~50 MB VRAM** (GPU) or CPU-only mode (~30ms per frame) |
| **Runs** | Locally |
| **Why MediaPipe** | Sub-millisecond on GPU, Google-maintained, excellent accuracy, tiny footprint, Python API. BlazeFace is purpose-built for real-time face detection. |
| **Team must learn** | MediaPipe Python API, face detection vs. recognition (we only need detection), confidence thresholds |

---

## I. Redaction / Masking

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Remove/mask all detected sensitive information from screenshots |
| **Inputs** | Original screenshot + list of sensitive regions |
| **Outputs** | Sanitized screenshot (safe to transmit to remote model) |
| **Technology** | **OpenCV / Pillow** for image manipulation |
| **Compute** | CPU-only, < 50ms |
| **Runs** | Locally |
| **Why OpenCV** | Fast, reliable, well-documented image operations (rectangle fill, Gaussian blur, pixelation) |
| **Team must learn** | Image manipulation (OpenCV/Pillow), different masking strategies, verification of complete redaction |

**Masking strategies by PII type:**
```python
REDACTION_STRATEGIES = {
    'password': 'black_rectangle',      # Solid black over field
    'email': 'black_rectangle',         # Solid black over text
    'phone': 'black_rectangle',         # Solid black over text  
    'face': 'gaussian_blur_40',         # Heavy Gaussian blur
    'aadhaar': 'black_with_placeholder',# "XXXX XXXX XXXX"
    'pan': 'black_with_placeholder',    # "XXXXXXXXXX"
    'credit_card': 'black_rectangle',   # Solid black
    'generic_pii': 'black_rectangle',   # Default: solid black
}
```

**Post-redaction verification:** Re-run PII detection on the sanitized image. If ANY PII is still detected → re-mask and log a warning.

---

## J. Local-vs-Cloud Routing

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Decide whether to handle a task step locally or send to remote model |
| **Inputs** | Task description, current step complexity, local model confidence, network status |
| **Outputs** | Routing decision {route: "local" | "remote", reason: string} |
| **Technology** | Rule-based decision tree (not ML — too simple to need a model) |
| **Compute** | Negligible (pure logic) |
| **Runs** | Locally |
| **Why rule-based** | Transparent, debuggable, no additional model needed. Can tune thresholds. |
| **Team must learn** | Decision tree design, confidence calibration |

**Routing rules:**
```python
def route_decision(task_step, local_confidence, network_ok):
    # Simple actions → always local
    if task_step.action_type in ['click', 'scroll', 'wait']:
        return 'local'
    
    # Network down → forced local
    if not network_ok:
        return 'local'
    
    # High local confidence → local
    if local_confidence > 0.85:
        return 'local'
    
    # Multi-step planning or low confidence → remote
    if task_step.requires_planning or local_confidence < 0.5:
        return 'remote'
    
    # Default: remote for safety
    return 'remote'
```

---

## K. Remote Reasoning Model

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Handle complex reasoning tasks using a large, capable model |
| **Inputs** | Sanitized screenshot + DOM summary + task + conversation history |
| **Outputs** | Next action command + reasoning explanation |
| **Technology** | **API call to Qwen3.8-Max / GPT-4o / Gemini** (team's choice based on availability) |
| **Alternatives** | Self-hosted larger model on Shaurya's Legion (if VRAM allows), Anthropic Claude API |
| **Compute** | Remote server — no local compute |
| **Runs** | **Remotely** (but only receives sanitized data) |
| **Why API** | For hackathon scope, running our own large model server is unnecessary. API is fastest path to strong reasoning. |
| **Team must learn** | API integration, prompt design for action generation, response parsing |

**Critical safety property:** The remote model NEVER receives:
- Raw screenshots (always sanitized)
- Actual password/email/phone values
- Face images (always blurred)
- Raw DOM with sensitive field values (values redacted in DOM summary)

---

## L. Agent Planner

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Orchestrate the entire agent loop — perception → decision → action → verification |
| **Inputs** | User task (natural language), system configuration |
| **Outputs** | Task completion status, action history, metrics |
| **Technology** | **Custom Python orchestrator** (not a framework — too simple to need one for hackathon) |
| **Alternatives** | LangChain/LangGraph (heavy dependency, not needed for a focused agent), smolagents (lighter but adds dependency) |
| **Compute** | CPU-only (pure orchestration logic) |
| **Runs** | Locally |
| **Why custom** | Agent loop is ~100 lines of Python. Framework overhead adds complexity without value at hackathon scale. |
| **Team must learn** | State machine design, retry logic, conversation memory management |

---

## M. Tool / Action Executor

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Parse model outputs into executable browser actions and execute them |
| **Inputs** | Structured action command from planner |
| **Outputs** | Execution result (success/failure) + new page state |
| **Technology** | Playwright commands wrapped in safety checks |
| **Compute** | CPU-only |
| **Runs** | Locally |
| **Why a separate module** | Isolates browser interaction from reasoning. Makes it testable and replaceable. |
| **Team must learn** | Action parsing (JSON → Playwright calls), error handling, timeout management |

---

## N. Action Verification

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Confirm that an executed action had the intended effect |
| **Inputs** | Before-screenshot, after-screenshot, expected outcome |
| **Outputs** | {verified: bool, changes_detected: list, confidence: float} |
| **Technology** | Screenshot diff (structural similarity) + VLM confirmation |
| **Compute** | ~100ms (image diff) + optional VLM call |
| **Runs** | Locally |
| **Why this matters** | Without verification, the agent can't self-correct. A click that misses its target looks like success without verification. |
| **Team must learn** | Image comparison techniques (SSIM, pixel diff), state change detection |

---

## O. Logging / Telemetry

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Record all agent actions, timings, decisions for debugging and demo |
| **Inputs** | Events from all modules |
| **Outputs** | Structured logs (JSON) + timing metrics |
| **Technology** | Python `logging` + custom metrics collector |
| **Compute** | Negligible |
| **Runs** | Locally |
| **Critical rule** | **NEVER log raw PII values.** Log redacted versions only. |
| **Team must learn** | Structured logging, metrics collection |

---

## P. Security / Privacy Layer

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Enforce privacy guarantees across the entire system |
| **Inputs** | All data flowing through the system |
| **Outputs** | Privacy compliance status, policy violations |
| **Technology** | Privacy gateway (validation middleware before any outbound call) |
| **Compute** | Negligible |
| **Runs** | Locally |
| **Why a dedicated layer** | Privacy is a cross-cutting concern. A single enforcement point is more auditable than scattered checks. |
| **Team must learn** | Gateway pattern, data flow analysis, India's DPDP Act basics |

---

## Q. Evaluation / Benchmarking

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Measure system performance across all dimensions |
| **Inputs** | Test scenarios, expected outcomes |
| **Outputs** | Benchmark results table |
| **Technology** | pytest + custom benchmark harness |
| **Compute** | Runs the full system |
| **Runs** | Locally |
| **Why critical** | ISRO evaluators want numbers, not claims. "Our system achieves 97% PII recall" is stronger than "we detect PII." |
| **Team must learn** | Precision/recall calculation, latency profiling, VRAM monitoring |
