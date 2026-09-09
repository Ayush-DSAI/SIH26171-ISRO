# PART 3 — TECH STACK SELECTION

---

## LANGUAGE: Python

**Decision: Python 3.11+**

| Option | Verdict | Reasoning |
|--------|---------|-----------|
| **Python** | ✅ CHOSEN | Entire ML ecosystem lives here. Transformers, llama.cpp bindings, MediaPipe, OpenCV, Playwright — all Python-first. Team's fastest path to a working prototype. |
| TypeScript/JS | ❌ Rejected | Weaker ML tooling. WebGPU inference is experimental. Would require bridging to Python for every ML component. Adds unnecessary complexity for a hackathon. |

**Note:** The demo frontend will use HTML/CSS/JS, but all backend/agent logic is Python.

---

## BROWSER AUTOMATION: Playwright (Python)

| Option | Speed | API Quality | Async | CDP Access | Vision Support | Verdict |
|--------|-------|-------------|-------|------------|---------------|---------|
| **Playwright** | Fast | Excellent | ✅ Native | ✅ Built-in | ✅ Screenshots | ✅ **CHOSEN** |
| Selenium | Slower | Legacy | ❌ Wrapper | ❌ Limited | ⚠️ Basic | ❌ Outdated |
| Raw CDP | Fastest | Low-level | ✅ | ✅ Direct | ✅ | ❌ Too much boilerplate |
| browser-use | Fast | High-level | ✅ | Via Playwright | ✅ | ⚠️ Consider for agent framework layer |

**Why Playwright wins:**
- `page.screenshot()` — instant viewport capture
- `page.accessibility.snapshot()` — structured DOM extraction
- `page.mouse.click(x, y)` — coordinate-based clicking (essential for grounding)
- `page.evaluate()` — run arbitrary JS for DOM queries
- Auto-wait — handles dynamic pages gracefully
- Headless + headed — headless for speed, headed for demo

**browser-use consideration:** browser-use is built ON TOP of Playwright and provides an agent framework. We could use it as our agent orchestration layer instead of writing our own. **Recommendation:** Start with raw Playwright for full control, evaluate browser-use as a potential accelerator in Week 2.

---

## VLM / MULTIMODAL MODEL SELECTION

### Primary: Qwen3.5-4B-Instruct (GGUF)

| Criterion | Qwen3.5-4B | SmolVLM 2.2B | MiniCPM-V 2.6 | Moondream2 |
|-----------|-----------|--------------|---------------|------------|
| **Parameters** | 4B | 2.2B | 8B | 1.7B |
| **VRAM @ Q4** | ~3.5 GB | ~2 GB | ~6–8 GB | ~1.5 GB |
| **Visual Grounding** | ✅ Strong | ⚠️ Basic | ✅ Strong | ⚠️ Basic |
| **OCR Capability** | ✅ Good | ⚠️ Fair | ✅ Excellent | ❌ Weak |
| **UI Understanding** | ✅ Good | ⚠️ Fair | ✅ Excellent | ⚠️ Fair |
| **Inference Speed** | ~300ms | ~150ms | ~600ms | ~100ms |
| **Ecosystem** | ✅ Qwen-Agent | ⚠️ HF only | ⚠️ Limited | ⚠️ Limited |
| **License** | Apache 2.0 | Apache 2.0 | Apache 2.0 | Apache 2.0 |
| **llama.cpp Support** | ✅ GGUF available | ✅ GGUF available | ✅ GGUF available | ✅ GGUF available |
| **8 GB Feasibility** | ✅ Comfortable | ✅ Very easy | ⚠️ Tight | ✅ Very easy |
| **Hackathon Suitability** | ✅ Best balance | ⚠️ Too weak for complex UI | ❌ VRAM too tight | ❌ Too weak |

**Verdict: Qwen3.5-4B is our primary model.** It delivers the best balance of capability, VRAM efficiency, and ecosystem support.

**Fallback strategy:**
1. If grounding accuracy is insufficient → try MiniCPM-V 2.6 (tighter on VRAM but stronger)
2. If VRAM is critically tight → fall back to SmolVLM 2.2B
3. Always maintain the option to swap models — our architecture is model-agnostic

### Quantization Format: GGUF Q4_K_M

| Format | Size Reduction | Quality Loss | Speed | Verdict |
|--------|---------------|-------------|-------|---------|
| FP16 | 1x (baseline) | None | Slow | ❌ Won't fit in 8GB |
| Q8_0 | ~2x | Minimal | Good | ⚠️ ~7GB, too tight |
| **Q4_K_M** | ~4x | Small (~2% degradation) | Fast | ✅ **CHOSEN** ~3.5GB |
| Q4_0 | ~4x | Moderate | Fastest | ⚠️ Backup if Q4_K_M too slow |
| Q2_K | ~6x | Significant | Fastest | ❌ Quality too low |

---

## VLM INFERENCE RUNTIME: llama.cpp (via llama-server)

| Runtime | GPU Support | VLM Support | GGUF | API Server | Easy Setup | Verdict |
|---------|------------|-------------|------|------------|------------|---------|
| **llama.cpp** | ✅ CUDA/Vulkan | ✅ mmproj | ✅ Native | ✅ OpenAI-compat | ✅ | ✅ **CHOSEN** |
| Transformers + PyTorch | ✅ CUDA | ✅ Full | ❌ | ❌ Manual | ⚠️ Heavy | ⚠️ Fallback |
| Ollama | ✅ | ✅ | ✅ | ✅ | ✅ Easiest | ⚠️ Less control |
| ONNX Runtime | ✅ | ⚠️ Limited VLM | ❌ | ❌ Manual | ⚠️ | ❌ VLM support immature |
| TensorRT-LLM | ✅ NVIDIA only | ✅ | ❌ | ✅ | ❌ Complex | ❌ Overkill for hackathon |

**Why llama.cpp:**
- Runs GGUF models natively (our quantization format)
- `llama-server` provides OpenAI-compatible API → easy integration
- Full multimodal support with `--mmproj` flag
- Fine-grained VRAM control (`--n-gpu-layers`, `--ctx-size`)
- Cross-platform (Windows, Linux)
- Single binary, no Python dependency hell

**Deployment command:**
```bash
llama-server \
  --model Qwen3.5-4B-Instruct-Q4_K_M.gguf \
  --mmproj Qwen3.5-4B-mmproj-f16.gguf \
  --port 8081 \
  --ctx-size 2048 \
  --n-gpu-layers 99 \
  --host 127.0.0.1
```

**Ollama as alternative:** If llama.cpp setup proves difficult, Ollama wraps it with a simpler UX. Trade-off: less control over VRAM and context settings.

---

## OCR ENGINE

| Option | Accuracy | Speed | VRAM | Languages | Verdict |
|--------|----------|-------|------|-----------|---------|
| **VLM built-in** | Good | 0ms extra | 0 extra | Multi | ✅ **MVP choice** |
| PaddleOCR (light) | Excellent | ~50ms | ~200MB | Multi | ✅ **Upgrade path** |
| Tesseract | Fair | ~200ms | CPU only | Multi | ⚠️ Slow, less accurate |
| EasyOCR | Good | ~150ms | ~500MB | Multi | ❌ Too heavy |

**Strategy:** Use VLM's built-in OCR for MVP. Add PaddleOCR if accuracy is insufficient for PII detection.

---

## FACE DETECTION

| Option | Speed | Accuracy | Size | GPU Support | Verdict |
|--------|-------|----------|------|-------------|---------|
| **MediaPipe BlazeFace** | <1ms GPU | Excellent | ~5MB | ✅ | ✅ **CHOSEN** |
| UltraLight ONNX | ~5ms | Good | ~1MB | ✅ ONNX | ⚠️ Backup |
| OpenCV Haar | ~20ms | Poor | ~1MB | ❌ CPU | ❌ Outdated |
| YOLO-Face | ~15ms | Excellent | ~50MB | ✅ | ❌ Overkill |

---

## PII DETECTION STACK

```
LAYER 1: DOM ATTRIBUTE SCANNING  ──→  ~5ms, CPU
         (input types, autocomplete, name/id patterns)

LAYER 2: REGEX ON DOM TEXT        ──→  ~10ms, CPU
         (Aadhaar with Verhoeff, PAN, email, phone, CC)

LAYER 3: OCR + REGEX ON IMAGE    ──→  ~100ms, GPU/CPU
         (for PII rendered as text in images/canvas)

LAYER 4 (STRETCH): GLiNER EDGE   ──→  ~100ms, CPU  
         (zero-shot NER for names, addresses)
```

**Indian PII patterns (verified):**
```python
PII_PATTERNS = {
    'aadhaar': r'\b[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}\b',  # + Verhoeff validation
    'pan': r'\b[A-Z]{5}\d{4}[A-Z]\b',
    'phone_in': r'(?:\+91[\s-]?)?[6-9]\d{9}\b',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'credit_card': r'\b(?:\d{4}[\s-]?){3}\d{4}\b',  # + Luhn validation
    'passport_in': r'\b[A-Z]\d{7}\b',
    'voter_id': r'\b[A-Z]{3}\d{7}\b',
}
```

---

## BACKEND / API

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Agent API** | **FastAPI** | REST endpoints for task submission, status, results |
| **VLM Server** | **llama-server** (llama.cpp) | OpenAI-compatible vision API on localhost |
| **WebSocket** | **FastAPI WebSocket** | Real-time agent status updates to demo UI |
| **Remote Model** | **HTTP client (httpx)** | Calls to cloud model API (GPT-4o/Qwen3.8-Max) |

**Why FastAPI:** Async-native, automatic OpenAPI docs, WebSocket support, lightweight. Perfect for hackathon.

**Architecture:**
```
Demo UI (browser) ←── WebSocket ──→ FastAPI Server ←── HTTP ──→ llama-server (local VLM)
                                         │
                                         ├── HTTP ──→ Remote Model API (cloud)
                                         │
                                         └── Playwright ──→ Target Browser
```

---

## FRONTEND / DEMO UI

| Technology | Purpose |
|-----------|---------|
| **HTML + CSS + Vanilla JS** | Demo dashboard showing agent workflow |
| **WebSocket client** | Real-time updates from agent |

**Demo UI shows:**
1. Original screenshot (left panel)
2. Detected PII regions highlighted (middle panel)
3. Sanitized screenshot (right panel)
4. Agent action log (bottom)
5. Latency/VRAM metrics (sidebar)
6. Current task status + progress

**No React/Vue needed.** The demo UI is a single page with panels. Vanilla JS + WebSocket is sufficient and avoids build tool overhead.

---

## DEPLOYMENT

```
LOCAL MACHINE (Shaurya's Legion or demo laptop):
├── llama-server (Qwen3.5-4B) ──→ GPU (CUDA)
├── FastAPI agent server ──→ CPU
├── Playwright browser instance ──→ CPU
├── MediaPipe face detection ──→ GPU/CPU
└── Demo UI ──→ served by FastAPI

REMOTE (only if hybrid path needed):
└── Cloud model API (GPT-4o / Qwen3.8-Max) ──→ already hosted, just API calls
```

**No Docker/K8s needed for hackathon.** Simple Python virtual environment + llama-server binary.

---

## VERSION CONTROL

| Aspect | Decision |
|--------|----------|
| **Platform** | GitHub (private repo) |
| **Branch strategy** | `main` (stable) + `dev` (integration) + feature branches per member |
| **PR workflow** | Feature branch → PR to `dev` → review by 1 person → merge |
| **Naming** | `feat/ayush-agent-loop`, `feat/abhishek-redaction`, etc. |
| **Commits** | Conventional commits: `feat:`, `fix:`, `docs:`, `test:` |
| **CI** | GitHub Actions: lint (ruff) + basic tests on PR |
| **.gitignore** | Model files (*.gguf), virtual environments, __pycache__, screenshots |
| **Model storage** | NOT in Git. Download script or Git LFS for small files only |

---

## DATABASE

**Decision: NO DATABASE for MVP.**

| Need | Solution |
|------|----------|
| Task history | JSON files (logs/) |
| Benchmark results | CSV/JSON files |
| Configuration | YAML config files |
| Model paths | Environment variables / config |

A database adds setup overhead with zero benefit for a hackathon prototype. SQLite can be added later if persistent task history is needed.

---

## COMPLETE STACK SUMMARY

```
┌─────────────────────────────────────────────┐
│              TECH STACK                      │
├─────────────────────────────────────────────┤
│ Language:        Python 3.11+               │
│ Browser:         Playwright                 │
│ VLM:             Qwen3.5-4B (Q4_K_M GGUF)  │
│ VLM Runtime:     llama-server (llama.cpp)   │
│ OCR:             VLM built-in → PaddleOCR   │
│ Face Detection:  MediaPipe BlazeFace        │
│ PII Detection:   DOM + Regex + OCR pipeline │
│ Image Processing:OpenCV + Pillow            │
│ Backend API:     FastAPI + WebSocket        │
│ Remote Model:    GPT-4o / Qwen3.8-Max API   │
│ Demo UI:         HTML + CSS + Vanilla JS    │
│ Version Control: GitHub + feature branches  │
│ Testing:         pytest                     │
│ Config:          YAML + env vars            │
│ Linting:         ruff                       │
│ Database:        None (JSON/CSV files)      │
└─────────────────────────────────────────────┘
```
