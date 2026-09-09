# PART 5 — INDIVIDUAL LEARNING CURRICULUMS

---

## AYUSH — System Integration + Agent Interface

### LEVEL 0: Prerequisites (Day 1)
- [ ] Python 3.11+ installed with virtual environment working
- [ ] VS Code + Python extensions
- [ ] Git + GitHub account configured
- [ ] Basic async/await in Python (you may have gaps here)
- **Exercise:** Write a Python async script that fetches 5 URLs in parallel using `asyncio` + `httpx`

### LEVEL 1: Concepts (Days 1–3)
| Concept | Why It Matters | What to Know | Depth | Exercise |
|---------|---------------|-------------|-------|----------|
| Agent loop pattern | This IS your module | Observe→Think→Act→Verify cycle, state management, retry logic | Advanced | Draw the full agent state machine on paper. Identify every transition. |
| VLM basics | You prompt the VLM | How VLMs take image+text→text, what grounding means | Intermediate | Read Qwen-VL model card. Write 5 different prompts for "describe this webpage." |
| Browser automation | You control the browser | Playwright Python API: navigate, click, type, screenshot, evaluate JS | Advanced | Automate a login flow on a test site using Playwright |
| Coordinate grounding | You translate VLM output to clicks | How (x,y) coords map to browser viewport, resolution scaling | Intermediate | Write code that takes a bounding box + screenshot and draws a red rectangle on it |
| Local/remote routing | You implement the decision | When to use local model vs remote, confidence thresholds | Intermediate | Write a decision-tree function with test cases |

### LEVEL 2: Tools (Days 3–5)
| Tool | Learn To | Output |
|------|----------|--------|
| Playwright | `page.goto()`, `page.screenshot()`, `page.mouse.click(x,y)`, `page.accessibility.snapshot()` | Working browser control script |
| FastAPI | Create REST endpoint + WebSocket endpoint | Server that accepts task, streams status via WS |
| httpx | Call OpenAI-compatible API (llama-server) | Client that sends image+prompt, gets text response |
| OpenCV/Pillow | Draw bounding boxes, overlay text, combine images | Side-by-side screenshot visualization |

### LEVEL 3: Mini-Project (Days 5–8)
**Build:** Complete agent loop prototype (without VLM — use mock responses)
- Takes a task string
- Opens browser, takes screenshot
- Sends screenshot to mock VLM (returns hardcoded "click at 300,400")
- Executes click
- Takes new screenshot
- Loops until mock says "done"
- Streams status to a simple WebSocket client

### LEVEL 4: Integration Task (Days 8–12)
- Replace mock VLM with Shaurya's llama-server
- Integrate Aditi's grounding module
- Insert Abhishek's redaction engine before remote calls
- Wire up Himanshu's logging/telemetry
- Build demo UI dashboard

### LEVEL 5: Jury Defense
**You MUST explain:**
1. The complete data flow from user task → browser action (with whiteboard)
2. How the agent handles a failed action (retry mechanism)
3. Why the architecture is modular and testable
4. How routing works (local fast path vs remote complex path)
5. Why Playwright over Selenium
6. How the demo UI reflects real-time agent state

---

## SHAURYA — Backend + Model Infrastructure

### LEVEL 0: Prerequisites (Day 1)
- [ ] CUDA toolkit installed on Legion
- [ ] Python 3.11+ with virtual environment
- [ ] nvidia-smi working and showing GPU
- [ ] Git configured
- [ ] llama.cpp cloned and compiled (with CUDA support)
- **Exercise:** Compile llama.cpp from source with CUDA. Verify with `llama-cli --help`

### LEVEL 1: Concepts (Days 1–3)
| Concept | Why It Matters | What to Know | Depth | Exercise |
|---------|---------------|-------------|-------|----------|
| VLM architecture | You serve the model | Vision encoder → projector → LLM, how images become tokens | Intermediate | Read Qwen3.5-VL architecture blog post. Draw the pipeline. |
| GGUF quantization | You choose quantization | FP16→Q8→Q4→Q2, quality vs size tradeoff, K-quants | Advanced | Download Q4_K_M and Q5_K_M of same model. Benchmark both. |
| VRAM management | You enforce the budget | GPU layers, context window size, KV cache, mmproj loading | Advanced | Run nvidia-smi while loading models. Document VRAM per component. |
| OpenAI API protocol | llama-server speaks this | /v1/chat/completions, image_url in messages, streaming | Intermediate | Call llama-server with curl and a test image |
| Image similarity metrics | For verification | SSIM, pixel diff, perceptual hashing | Intermediate | Compute SSIM between two screenshots in Python |

### LEVEL 2: Tools (Days 3–5)
| Tool | Learn To | Output |
|------|----------|--------|
| llama-server | All CLI flags: --model, --mmproj, --ctx-size, --n-gpu-layers, --port | Running server with verified vision capability |
| nvidia-smi | Monitor VRAM in real-time, log GPU utilization | VRAM usage log during inference |
| Python httpx | Async calls to llama-server and remote APIs | API client wrapper class |
| OpenCV | SSIM calculation, image comparison | Verification function |

### LEVEL 3: Mini-Project (Days 5–8)
**Build:** Local VLM inference benchmarking tool
- Load Qwen3.5-4B Q4_K_M via llama-server
- Send 20 different webpage screenshots
- Measure: inference time, VRAM usage, output quality
- Test at 720p, 1080p resolutions
- Compare Q4_K_M vs Q5_K_M
- Document as a benchmark report

### LEVEL 4: Integration Task (Days 8–12)
- Optimize inference for < 500ms target
- Integrate remote model API client (with sanitized input validation)
- Implement verification module (before/after screenshot diff)
- Set up VRAM monitoring that feeds into Himanshu's telemetry

### LEVEL 5: Jury Defense
**You MUST explain:**
1. Why Qwen3.5-4B Q4_K_M and not another model (with numbers)
2. Exact VRAM breakdown of every component
3. How quantization works (Q4_K_M specifically)
4. Inference latency numbers at different resolutions
5. How llama-server provides an OpenAI-compatible API
6. What happens when VRAM runs out (OOM handling)

---

## HIMANSHU — Networking + API + Architecture

### LEVEL 0: Prerequisites (Day 1)
- [ ] Python 3.11+ with virtual environment
- [ ] Postman or Thunder Client installed
- [ ] Basic HTTP protocol understanding (GET, POST, headers, status codes)
- [ ] Git configured
- **Exercise:** Create a FastAPI server with one GET and one POST endpoint. Test with Postman.

### LEVEL 1: Concepts (Days 1–3)
| Concept | Why It Matters | What to Know | Depth | Exercise |
|---------|---------------|-------------|-------|----------|
| REST API design | You design all APIs | Resource naming, HTTP methods, status codes, request/response schemas | Advanced | Design the API spec for the agent (endpoints for submit task, get status, get results) |
| WebSocket protocol | Real-time agent updates | Connection lifecycle, message framing, when WS vs REST | Intermediate | Build a WS echo server + HTML client |
| Data flow security | Core privacy guarantee | What data moves where, TLS, authentication | Advanced | Trace every piece of data in our system. Mark sensitive vs safe. |
| Structured logging | Debugging + demo telemetry | JSON log format, log levels, PII-safe formatting | Intermediate | Set up Python logging with JSON formatter that masks emails |
| System architecture diagrams | Jury presentation | Component diagrams, sequence diagrams, data flow diagrams | Advanced | Draw our full architecture using Mermaid or draw.io |

### LEVEL 2: Tools (Days 3–5)
| Tool | Learn To | Output |
|------|----------|--------|
| FastAPI | REST + WebSocket + middleware + CORS | API server skeleton with all endpoints |
| Pydantic | Request/response validation schemas | Type-safe API models |
| Python logging | Structured JSON logs + PII filter | Logging module ready to integrate |
| Mermaid/draw.io | Professional architecture diagrams | 3+ diagrams for PPT |

### LEVEL 3: Mini-Project (Days 5–8)
**Build:** Privacy gateway + telemetry collector
- FastAPI middleware that inspects outbound requests
- Validates no raw PII in request body/headers
- Blocks requests that fail validation
- Collects timing data from tagged code sections
- Exposes /metrics endpoint
- Logs everything in structured JSON

### LEVEL 4: Integration Task (Days 8–12)
- Connect privacy gateway to Ayush's agent loop
- Hook telemetry collection into all modules
- Create architecture diagrams reflecting actual implementation
- Validate privacy claim: run test, show logs proving no raw PII left device

### LEVEL 5: Jury Defense
**You MUST explain:**
1. Complete data flow diagram (what moves where, when)
2. Privacy guarantee: how we PROVE no raw PII leaves the device
3. API design decisions and endpoint structure
4. Latency contribution of networking (local inference vs remote call)
5. How WebSocket streams real-time agent status to demo UI
6. Security model (TLS, no-log policy for PII)

---

## ADITI — ML/VLM Research + Grounding

### LEVEL 0: Prerequisites (Day 1)
- [ ] Python 3.11+ with virtual environment
- [ ] PyTorch installed (CPU is fine for understanding; GPU preferred)
- [ ] Hugging Face account, `huggingface-cli` configured
- [ ] Jupyter notebook setup
- **Exercise:** Load any Hugging Face text model, run inference. Understand tokenizer→model→output pipeline.

### LEVEL 1: Concepts (Days 1–4)
| Concept | Why It Matters | What to Know | Depth | Exercise |
|---------|---------------|-------------|-------|----------|
| Vision-Language Model architecture | You select and evaluate the model | Vision encoder (ViT/SigLIP), projection layer, LLM decoder, how images become tokens | Advanced | Read QwenVL technical report. Diagram the architecture from image pixels to text output. |
| Visual grounding | Core capability you build | How models output bounding boxes, coordinate formats (normalized vs pixel, xyxy vs xywh), Set-of-Mark prompting | Advanced | Given a screenshot, manually annotate 10 elements with bounding boxes. Compare with model output. |
| Prompt engineering for VLMs | Directly impacts accuracy | System prompts, few-shot examples, structured output formatting, grounding-specific prompts | Advanced | Write 10 prompt variants for "locate the search button" and test accuracy |
| Quantization effects | You verify model quality holds | How Q4 impacts vision accuracy, what to check | Intermediate | Compare FP16 vs Q4 outputs on same 10 screenshots, measure coordinate drift |
| OCR with VLMs | Dual-use for text extraction | How VLMs can read text from images, accuracy limits | Intermediate | Test VLM's ability to read all text from a complex webpage screenshot |
| Evaluation metrics | You measure everything | IoU (Intersection over Union) for grounding, accuracy, precision@k | Advanced | Implement IoU calculation in Python. Score model grounding on 20 test images. |

### LEVEL 2: Tools (Days 4–6)
| Tool | Learn To | Output |
|------|----------|--------|
| Hugging Face Hub | Search models, read model cards, download weights | Comparison document of 3 VLM candidates |
| llama-server API | Send vision requests programmatically | Python wrapper: `ground_element(image, description) → bbox` |
| OpenCV | Draw bounding boxes, visualize grounding results | Visual grounding test report with annotated images |
| Jupyter | Rapid experimentation with prompt variants | Notebook: prompt_comparison.ipynb |

### LEVEL 3: Mini-Project (Days 6–9)
**Build:** Visual grounding module
- Input: screenshot (PIL Image) + element description (string)
- Process: Send to llama-server with grounding prompt
- Parse: Extract bounding box from model response
- Output: `{element, bbox: [x, y, w, h], confidence}`
- Test on 20+ different webpage screenshots
- Measure IoU against manual annotations
- Compare 3 different prompt strategies

### LEVEL 4: Integration Task (Days 9–13)
- Integrate grounding module into Ayush's agent loop
- Add DOM-based fallback grounding (when VLM coordinates are uncertain)
- Optimize prompt for best accuracy/speed tradeoff
- Create grounding accuracy evaluation report

### LEVEL 5: Jury Defense
**You MUST explain:**
1. How a VLM processes an image (vision encoder → tokens → LLM)
2. What grounding is and how our model achieves it
3. Why Qwen3.5-4B was chosen (with comparative benchmarks)
4. How quantization affects vision accuracy (with evidence)
5. What Set-of-Mark prompting is and when we use it
6. How DOM fallback complements VLM grounding
7. IoU scores and what they mean

---

## ABHISHEK — Privacy + Redaction + Testing

### LEVEL 0: Prerequisites (Day 1)
- [ ] Python 3.11+ with virtual environment
- [ ] OpenCV + Pillow installed
- [ ] MediaPipe installed (`pip install mediapipe`)
- [ ] Basic regex knowledge
- **Exercise:** Write a regex that matches Indian phone numbers (with and without +91). Test on 20 examples.

### LEVEL 1: Concepts (Days 1–3)
| Concept | Why It Matters | What to Know | Depth | Exercise |
|---------|---------------|-------------|-------|----------|
| Indian PII formats | Core detection targets | Aadhaar (12-digit + Verhoeff), PAN (AAAAA0000A), phone, email, passport | Advanced | Create a reference sheet of all Indian PII formats with validation rules |
| Regex patterns | Primary detection tool | Python `re` module, lookahead/behind, special characters, performance | Advanced | Write and test regex for Aadhaar, PAN, email, phone, credit card |
| Verhoeff algorithm | Aadhaar validation | How the checksum validates the 12th digit | Intermediate | Implement Verhoeff in Python. Test with valid/invalid Aadhaar numbers. |
| Face detection | Visual PII | How BlazeFace works (high level), detection vs recognition, confidence thresholds | Intermediate | Run MediaPipe on 10 images with varying face sizes/angles. Measure detection rate. |
| Image redaction | Removing PII from screenshots | Rectangle overlay, Gaussian blur, pixelation, alpha compositing | Intermediate | Implement 4 different redaction styles in OpenCV |
| Precision/recall | Measuring detection quality | True/false positives/negatives, F1 score, why recall > precision for privacy | Advanced | Calculate P/R/F1 on a test set of 50 text samples |
| DOM attribute scanning | Cheapest PII signal | HTML input types, autocomplete values, form field naming conventions | Intermediate | Write a Playwright script that extracts all input fields and their attributes |

### LEVEL 2: Tools (Days 3–5)
| Tool | Learn To | Output |
|------|----------|--------|
| Python `re` | Compile patterns, findall, sub, groups | PII regex library module |
| MediaPipe | Face detection API, confidence thresholding | Face detection wrapper function |
| OpenCV | Rectangle, blur, mask, copy, paste regions | Redaction function library |
| pytest | Write test cases, fixtures, parameterized tests | Test suite skeleton |
| Playwright | Extract DOM attributes, evaluate JS | DOM scanner function |

### LEVEL 3: Mini-Project (Days 5–8)
**Build:** Complete PII detection + redaction engine
- Input: screenshot (image) + DOM tree (JSON)
- Layer 1: DOM scan for sensitive attributes
- Layer 2: Regex scan on DOM text content
- Layer 3: Face detection on screenshot
- Output: list of sensitive regions + sanitized screenshot
- Verify: re-scan sanitized image → should find 0 PII
- Benchmark: measure precision, recall, latency

### LEVEL 4: Integration Task (Days 8–12)
- Plug redaction engine into Ayush's agent loop
- Handle Aditi's OCR output for image-based PII detection
- Run full benchmark suite on Nidhi's test web pages
- Document all benchmark results with evidence

### LEVEL 5: Jury Defense
**You MUST explain:**
1. All PII detection layers and why each is needed
2. What Verhoeff checksum is and why regex alone isn't enough for Aadhaar
3. Precision vs recall tradeoff — why we prioritize recall for privacy
4. How face detection works (BlazeFace, high-level)
5. What happens when PII appears in an image (not in DOM)
6. Benchmark results: detection rate, false positives, latency
7. Post-redaction verification step

---

## NIDHI — QA + Documentation + Demo

### LEVEL 0: Prerequisites (Day 1)
- [ ] Python 3.11+ installed (basic usage)
- [ ] VS Code installed
- [ ] Git basics: clone, pull, push, commit (practice with a test repo)
- [ ] Markdown syntax (headers, tables, code blocks, lists)
- **Exercise:** Create a GitHub repo, add a README.md with proper formatting, make 3 commits.

### LEVEL 1: Concepts (Days 1–3)
| Concept | Why It Matters | What to Know | Depth | Exercise |
|---------|---------------|-------------|-------|----------|
| Browser agent (what it does) | You explain this to non-technical jury | Agent sees a webpage, understands it, takes actions, respects privacy | Basic | Write a 1-paragraph explanation of our system for a non-engineer. |
| Privacy/redaction flow | You demonstrate this in the demo | What PII is, how we detect it, how we mask it, before/after | Basic-Intermediate | Create a flowchart of the redaction pipeline |
| Test case design | You create test scenarios | What to test, boundary cases, expected vs actual results | Intermediate | Design 10 test cases for "Does the system detect email addresses?" |
| System architecture (overview) | You may be asked by judges | Modules, data flow, local vs remote | Basic | Draw the architecture from memory (simplified version) |
| HTML basics | You create test pages | Forms, inputs, images, basic page structure | Basic-Intermediate | Create 3 HTML pages with different PII types |

### LEVEL 2: Tools (Days 3–5)
| Tool | Learn To | Output |
|------|----------|--------|
| HTML/CSS (basic) | Create test web pages with forms, images, text | 5 test pages with PII |
| Markdown | Write documentation, tables, formatting | README draft |
| GitHub Issues | Create issues, assign, label, track | Populated issue board |
| Screenshot tools | Record demo video, capture results | Demo recording setup |
| Spreadsheets | Collect and format benchmark data | Results template |

### LEVEL 3: Mini-Project (Days 5–8)
**Build:** Test suite + documentation package
- 10 HTML test pages covering all PII scenarios:
  - Page with password field + email field
  - Page with Aadhaar number in text
  - Page with face photo
  - Page with PAN card image
  - Page with credit card form
  - Page with phone number in footer
  - Complex form with mixed PII
  - Page with NO PII (negative test)
  - Dynamic page with JS-rendered PII
  - Dark mode page
- Test scenario matrix (expected detection for each page)
- Written demo script (timing, narration, what to show)

### LEVEL 4: Integration Task (Days 8–12)
- Run Abhishek's redaction engine on all 10 test pages
- Document results (detected ✅ / missed ❌ for each PII element)
- Collect benchmark numbers from all team members
- Format into presentation-ready tables and charts
- Write final README.md and setup guide

### LEVEL 5: Jury Defense
**You MUST explain:**
1. What the system does (1-minute elevator pitch)
2. What test scenarios were covered
3. High-level privacy guarantee (non-technical version)
4. Demo walkthrough narration
5. How we validated our claims (point to specific benchmarks)
