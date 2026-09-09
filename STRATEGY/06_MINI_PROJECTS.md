# PART 6 — MINI-PROJECTS (Standalone → Integration)

---

## Overview

Each member builds a **standalone prototype** in Days 5–8 that later plugs into the final system. These are designed to:
1. Force hands-on learning of the assigned module
2. Produce a testable, working component
3. Have clear input/output interfaces for integration

---

## MINI-PROJECT A: Agent Loop + Browser Control (AYUSH)

| Attribute | Detail |
|-----------|--------|
| **Objective** | Build a working agent loop that controls a browser using mock VLM responses |
| **Inputs** | Task string (e.g., "Search for 'ISRO' on Google"), mock VLM responses |
| **Expected Output** | Agent opens browser → takes screenshot → receives mock action → executes action → takes new screenshot → loops until "done" |
| **Stack** | Python, Playwright, FastAPI, WebSocket |
| **Duration** | 3 days |

**Success Criteria:**
- [ ] Opens browser and navigates to a URL
- [ ] Takes a screenshot and saves it
- [ ] Sends screenshot to a mock endpoint (returns hardcoded action)
- [ ] Parses action JSON → executes Playwright command
- [ ] Loops 3–5 times on a real website (e.g., Google search)
- [ ] Streams agent status via WebSocket to an HTML page
- [ ] Gracefully handles: element not found, page timeout, max iterations

**Stretch Goal:** Replace mock with actual llama-server call (coordinate with Shaurya).

**Integration Point:** This becomes the central orchestrator. Every other module plugs into this loop.

**Estimated Difficulty:** 6/10

---

## MINI-PROJECT B: VLM Inference Server + Benchmarks (SHAURYA)

| Attribute | Detail |
|-----------|--------|
| **Objective** | Deploy Qwen3.5-4B locally, benchmark latency/accuracy at different quantizations |
| **Inputs** | GGUF model files, 20 webpage screenshots |
| **Expected Output** | Running llama-server with benchmarks: latency per quantization, VRAM usage |
| **Stack** | llama.cpp (server), Python benchmark script, nvidia-smi |
| **Duration** | 3 days |

**Success Criteria:**
- [ ] llama-server running with Qwen3.5-4B Q4_K_M + mmproj
- [ ] Can send an image + prompt via curl and get a text response
- [ ] Benchmark 20 screenshots: measure inference time (min/avg/max)
- [ ] Compare Q4_K_M vs Q5_K_M (latency + quality)
- [ ] Document VRAM usage at different context sizes
- [ ] Test resolution impact: 720p vs 1080p ims + latency
- [ ] Produce benchmark report (markdown + CSV)

**Stretch Goal:** Set up Ollama as alternative runtime. Compare latency against llama-server.

**Integration Point:** Ayush's agent loop calls this server's `/v1/chat/completions` endpoint.

**Estimated Difficulty:** 7/10

---

## MINI-PROJECT C: Visual Grounding Module (ADITI)

| Attribute | Detail |
|-----------|--------|
| **Objective** | Build a module that takes a screenshot + element description → returns bounding box coordinates |
| **Inputs** | Screenshot image (PIL/path) + element description string |
| **Expected Output** | `{element: "Login button", bbox: [x, y, w, h], confidence: float}` |
| **Stack** | Python, httpx (to call llama-server), OpenCV (to draw boxes), Jupyter |
| **Duration** | 3 days |

**Success Criteria:**
- [ ] Sends screenshot + grounding prompt to llama-server
- [ ] Parses bounding box coordinates from VLM response
- [ ] Handles multiple coordinate formats (xyxy, xywh, normalized, pixel)
- [ ] Visualizes grounding results (annotated screenshots with boxes)
- [ ] Tests on 20 screenshots: buttons, inputs, links, images, text
- [ ] Calculates IoU against manual annotations for 10 elements
- [ ] Documents best prompt strategy

**Stretch Goal:** Implement Set-of-Mark prompting (overlay numbered labels on elements, ask VLM to identify by number).

**Integration Point:** Ayush's agent loop calls `ground_element(screenshot, "submit button")` before executing a click.

**Estimated Difficulty:** 8/10

---

## MINI-PROJECT D: PII Detection + Redaction Engine (ABHISHEK)

| Attribute | Detail |
|-----------|--------|
| **Objective** | Build a complete PII detection + redaction pipeline |
| **Inputs** | Screenshot image + DOM tree JSON |
| **Expected Output** | List of detected PII regions + sanitized screenshot |
| **Stack** | Python, regex, MediaPipe, OpenCV, Pillow, Playwright (for DOM extraction) |
| **Duration** | 3 days |

**Success Criteria:**
- [ ] DOM scanner detects: password, email, phone, credit card fields by attribute
- [ ] Regex detects: Aadhaar (with Verhoeff), PAN, email, phone in text
- [ ] MediaPipe detects faces in screenshots
- [ ] Redaction applies appropriate mask per PII type (black rect, blur, etc.)
- [ ] Post-redaction verification: re-scan sanitized image confirms no PII
- [ ] Produces before/after comparison image
- [ ] Measures: precision, recall, latency per detection layer
- [ ] Test suite: 30+ test cases (positive + negative)

**Stretch Goal:** Add OCR layer (PaddleOCR or VLM) for PII rendered as text in images.

**Integration Point:** Ayush's agent loop calls `redact(screenshot, dom)` before sending to remote model.

**Estimated Difficulty:** 7/10

---

## MINI-PROJECT E: Privacy Gateway + Telemetry (HIMANSHU)

| Attribute | Detail |
|-----------|--------|
| **Objective** | Build a FastAPI middleware that validates outbound data privacy + collects timing metrics |
| **Inputs** | Outbound HTTP requests from the agent, timing events from modules |
| **Expected Output** | Blocked/allowed requests with audit log + timing dashboard |
| **Stack** | Python, FastAPI, structured logging, Pydantic |
| **Duration** | 3 days |

**Success Criteria:**
- [ ] FastAPI middleware inspects all outbound requests
- [ ] Scans request body for PII patterns (email, phone, etc.)
- [ ] BLOCKS requests containing detected raw PII (returns 403 with reason)
- [ ] Structured JSON logs for every request (with PII-safe output)
- [ ] Timing collector: accepts timing events, stores in memory
- [ ] `/metrics` endpoint returns latency breakdown by module
- [ ] `/audit` endpoint returns privacy validation log
- [ ] Demo: show a request being blocked because it contains an email

**Stretch Goal:** Add Wireshark capture to prove no PII in network traffic.

**Integration Point:** Wraps all outbound HTTP calls from the agent to remote models.

**Estimated Difficulty:** 5/10

---

## MINI-PROJECT F: Test Suite + Documentation Package (NIDHI)

| Attribute | Detail |
|-----------|--------|
| **Objective** | Create test web pages, scenario matrix, demo script, and project documentation |
| **Inputs** | Architecture knowledge from team, PII formats from Abhishek |
| **Expected Output** | 10 test HTML pages + scenario matrix + demo script + README |
| **Stack** | HTML/CSS, Markdown, GitHub Issues |
| **Duration** | 3 days |

**Success Criteria:**
- [ ] 10 test HTML pages with varied PII (see list below)
- [ ] Test scenario matrix: for each page, list expected detections
- [ ] Written demo script (3–5 minutes, with exact timing)
- [ ] Project README.md with: overview, setup instructions, architecture diagram
- [ ] GitHub Issues board with tasks for all members
- [ ] Demo recording plan: what to capture, what to say

**Test Page Specifications:**
```
Page 1:  Login form (username + password + email)
Page 2:  Registration form (name, phone, email, Aadhaar field)
Page 3:  Profile page with face photo + name + email
Page 4:  Payment form (credit card, CVV, billing address)
Page 5:  Government form (PAN, Aadhaar, voter ID fields)
Page 6:  Social media profile (face, phone in bio, email in footer)
Page 7:  Search results page with no PII (negative test)
Page 8:  Complex form with dynamically shown/hidden fields
Page 9:  Dark mode page with PII
Page 10: Page with PII inside an image (e.g., scanned Aadhaar card)
```

**Stretch Goal:** Create an animated demo video showing the redaction flow.

**Integration Point:** These test pages become the primary evaluation set for benchmarking.

**Estimated Difficulty:** 3/10

---

## MINI-PROJECT DEPENDENCY CHAIN

```
Week 1 (parallel, no dependencies):
├── Shaurya: VLM server setup ──────────────────────┐
├── Aditi: Grounding prompts (can use Shaurya's server) ──┤
├── Abhishek: Redaction engine (standalone) ─────────┤
├── Himanshu: Privacy gateway (standalone) ──────────┤
├── Nidhi: Test pages + docs (standalone) ───────────┤
└── Ayush: Agent loop with mocks (standalone) ───────┘
                                                      │
Week 2 (integration, dependencies emerge):            ▼
├── Ayush replaces mocks with Shaurya's server ───── Integration starts
├── Ayush adds Aditi's grounding to the loop
├── Ayush adds Abhishek's redaction before remote calls
├── Himanshu wraps outbound calls with privacy gateway
├── Abhishek runs redaction on Nidhi's test pages
└── Everyone tests against Nidhi's test scenario matrix
```

---

## MINI-PROJECT SUBMISSION TEMPLATE

Each member should submit their mini-project with:

```
/mini-project-[name]/
├── README.md          # What it does, how to run, success criteria met
├── src/               # Source code
├── tests/             # Test cases
├── results/           # Screenshots, benchmarks, logs
└── INTEGRATION.md     # How this plugs into the main system
                       # (input format, output format, API endpoint)
```
