# PART 1 — UNDERSTAND THE PROBLEM

---

## 1. What the PS Is Actually Asking Us to Build

ISRO wants a **browser automation agent** that runs primarily on-device (on hardware with ~8 GB VRAM) and can:
- **See** web pages visually (not just parse HTML)
- **Understand** what UI elements mean and where they are
- **Act** on the browser (click buttons, fill forms, navigate)
- **Protect privacy** by never sending raw sensitive data off-device

This is NOT a chatbot. This is NOT a simple web scraper. This is an **autonomous agent** that takes a natural-language instruction (e.g., "Book a train ticket from Delhi to Mumbai for tomorrow") and executes it by visually understanding and interacting with actual web interfaces — while keeping your passwords, Aadhaar numbers, and face photos private.

**Why ISRO cares:** Space agencies use internal web tools, dashboards, procurement portals. An on-device agent that can automate browser workflows WITHOUT leaking sensitive organizational data to cloud providers is strategically valuable.

---

## 2. What "Visual Perception for Browser Agents" Means

Traditional browser automation (Selenium scripts) relies on **CSS selectors and XPaths** — brittle strings like `#login-btn` that break when a website updates its HTML.

**Visual perception** means the agent looks at a **screenshot** of the webpage (like a human would) and understands:
- Where is the login button?
- What does this form ask for?
- Which element should I click next?

This is powered by **Vision-Language Models (VLMs)** — AI models that take an image + text prompt and return text understanding.

**Why this matters:** Visual perception is robust to UI changes, works on any website (even ones with complex JavaScript rendering), and mimics how humans actually use browsers.

---

## 3. What "Grounding" Means in This Context

**Grounding** = mapping a natural-language description to a **specific pixel location or bounding box** on the screen.

Example:
- Input: "the Submit button" + screenshot
- Output: `[x: 450, y: 320, width: 120, height: 40]` — the exact coordinates of the Submit button

Without grounding, the model can describe what it sees but cannot **act** on it. Grounding is what makes the agent operational, not just observational.

**Types of grounding we need:**
- **Element grounding:** "Click the search bar" → coordinates of the search bar
- **Text grounding:** "The email field" → location of the email input
- **Semantic grounding:** "The primary CTA" → understanding that a large colored button is the main call-to-action

---

## 4. What "Lightweight VLM" Means

A **VLM (Vision-Language Model)** is a neural network that jointly processes images and text. Examples: GPT-4o, Gemini Pro Vision, Qwen-VL.

**"Lightweight"** means:
- **Parameter count:** 2B–8B parameters (vs. 70B+ for large models)
- **VRAM requirement:** Fits in 3–8 GB with quantization (vs. 40+ GB for large models)
- **Inference speed:** < 1 second per screenshot (vs. 3–10 seconds for cloud roundtrips)
- **Deployment:** Runs LOCALLY on a laptop/desktop GPU

**Our primary candidate: Qwen3.5-4B (Instruct)**
- 4B parameters
- ~3.5 GB VRAM at Q4_K_M quantization
- Strong visual grounding capability
- Active ecosystem (Qwen-Agent framework)
- Apache 2.0 license

---

## 5. What an "Agent Loop" Means

An agent loop is the core execution cycle:

```
OBSERVE → THINK → ACT → VERIFY → REPEAT
```

Concretely:
1. **OBSERVE:** Take a screenshot + extract DOM
2. **THINK:** Send observation to VLM with the task instruction → get reasoning + next action
3. **ACT:** Execute the action (click, type, scroll) via Playwright
4. **VERIFY:** Take another screenshot → did the action succeed?
5. **REPEAT:** If task not complete, go to step 1

This loop continues until:
- The task is completed successfully
- A maximum number of iterations is reached (safety limit)
- An unrecoverable error occurs

**Key design decision:** Each iteration should be fast (< 2 seconds ideally) so the agent doesn't feel sluggish.

---

## 6. Why an On-Device Model Is Valuable

| Advantage | Explanation |
|-----------|-------------|
| **Privacy** | Screenshots contain passwords, emails, financial data. On-device = never leaves your machine. |
| **Latency** | No network roundtrip. Local inference in 200–500ms vs. 1–5s for cloud API. |
| **Cost** | No per-token API charges. Once deployed, inference is free. |
| **Availability** | Works offline or in restricted networks (ISRO internal networks). |
| **Control** | No dependency on third-party API availability or rate limits. |
| **Compliance** | Satisfies data residency requirements (critical for government/defense). |

---

## 7. Why 8 GB VRAM Is an Important Design Constraint

8 GB VRAM is the most common GPU configuration in consumer/prosumer hardware (RTX 3060, RTX 4060, Legion laptops). This constraint means:

**What fits:**
- Qwen3.5-4B @ Q4: ~3.5 GB
- MediaPipe face detection: ~50 MB
- OCR engine: ~100 MB
- Screenshot buffer: ~50 MB
- Total: **~4 GB** — leaves ~4 GB headroom for KV cache, OS overhead, browser

**What does NOT fit:**
- LLaMA 70B (requires 35+ GB)
- GPT-4o (cloud-only)
- Any unquantized 7B+ model (14+ GB in FP16)

**Design implication:** We MUST use quantized models and cannot load multiple large models simultaneously. This drives the hybrid architecture — light model locally, heavy model remotely.

---

## 8. Why Latency Matters

Each agent loop iteration involves:
- Screenshot capture: ~50ms
- DOM extraction: ~100ms
- VLM inference: ~200–500ms (local) or 1–5s (cloud)
- Action execution: ~100ms

A typical task (e.g., "search for flights") might take 5–15 iterations.

| Architecture | Per-Iteration | 10-Iteration Task |
|-------------|--------------|-------------------|
| Fully cloud | 2–6s | 20–60s |
| Fully local | 0.5–1s | 5–10s |
| Hybrid (ours) | 0.5–3s | 5–30s |

**Users will not wait 60 seconds for a browser agent to fill a form.** Low latency is a competitive requirement, not just a nice-to-have.

---

## 9. Why Browser DOM Complements Visual Perception

**DOM (Document Object Model)** is the structured HTML tree of a webpage. It provides:

| Information | From DOM | From Vision |
|-------------|----------|-------------|
| Input field type | `<input type="password">` ✅ | Hard to distinguish visually ❌ |
| Button text | `<button>Submit</button>` ✅ | OCR needed, may misread ⚠️ |
| Hidden elements | `display:none` detected ✅ | Invisible ❌ |
| Dropdown options | All `<option>` values ✅ | Must click to see ❌ |
| **Visual layout** | CSS math needed ❌ | Screenshot shows it ✅ |
| **Custom components** | Non-standard HTML ❌ | Looks like a button visually ✅ |
| **Canvas/WebGL** | No DOM structure ❌ | Visual understanding ✅ |

**The hybrid DOM + Vision approach catches what either alone misses.** This is one of our key architectural advantages.

**Critical for privacy:** DOM tells us `type="password"` directly — no need for ML to detect password fields. This is the cheapest, most reliable PII signal we have.

---

## 10. Why Hybrid Local + Remote Is Stronger Than Just Cloud

| Approach | Pros | Cons |
|----------|------|------|
| **Cloud-only** | Most capable model, best reasoning | Privacy disaster, high latency, cost, network dependency |
| **Local-only** | Maximum privacy, lowest latency | Limited reasoning capability (4B << 400B) |
| **Hybrid (ours)** | Privacy preserved, strong reasoning when needed, fast for simple tasks | More complex architecture |

**The hybrid architecture gives us the best of both worlds:**
- Simple tasks (click a button, fill a known field) → handled locally in < 500ms
- Complex tasks (multi-step reasoning, understanding a new workflow) → sanitized screenshot sent to remote model
- Privacy is ALWAYS preserved because the remote model never sees raw PII

**This is the architecture ISRO is specifically asking for.** The PS description explicitly mentions "privacy-preserving hybrid architecture."

---

## 11. Hardest Technical Challenges

### Tier 1: Critical (Must Solve)
1. **Reliable redaction** — If we miss even ONE password field, our privacy claim is broken
2. **Accurate grounding** — If the model clicks the wrong button, the task fails
3. **VRAM management** — Loading VLM + face detection + OCR within 8 GB simultaneously
4. **Agent loop stability** — Self-correcting when actions fail, not getting stuck in loops

### Tier 2: Hard (Should Solve)
5. **Dynamic pages** — SPAs that change DOM after JavaScript execution
6. **PII in images** — Aadhaar card photos, ID scans rendered as `<img>` tags
7. **Non-standard UI** — Custom React components, shadow DOM, canvas-based UIs
8. **Redaction accuracy** — Not over-redacting (making the screenshot useless for reasoning)

### Tier 3: Edge Cases (Nice to Handle)
9. **CAPTCHAs** — Detect and report, not attempt to solve
10. **Prompt injection** — Webpage contains text that tries to hijack the agent
11. **Iframes** — Embedded content from different origins
12. **Browser zoom/scale** — Coordinates shift with zoom level

---

## 12. What Distinguishes Mediocre from Impressive

### MEDIOCRE Submission:
- Uses cloud API directly with raw screenshots
- Simple Selenium script with hardcoded selectors
- "We redact PII" but no demonstration of detection accuracy
- No benchmarks, just a demo video
- Only works on one pre-selected website
- No fallback when things go wrong

### IMPRESSIVE Submission (What We Must Build):
- **Visually demonstrates** original → detected → redacted → sanitized flow
- **Benchmarks** redaction precision/recall with specific numbers
- **Shows latency breakdown** for each pipeline stage
- **Works on multiple unseen websites** (not just pre-trained demos)
- **Handles edge cases** gracefully (pop-ups, dynamic content, missing DOM)
- **Privacy claims backed by measurement** ("99.2% PII recall on our test set")
- **Architecture diagram** that an ISRO engineer would find credible
- **Fallback behavior** when remote server is unreachable
- **Resource utilization dashboard** showing VRAM/RAM/CPU in real-time

---

## END-TO-END PIPELINE (Every Stage Explained)

```
STAGE 1: BROWSER
├── Playwright controls a Chromium browser instance
├── Maintains session, cookies, authentication state
└── Exposes CDP (Chrome DevTools Protocol) for fine-grained control

STAGE 2: SCREEN/DOM OBSERVATION
├── Screenshot: Full-page PNG capture via CDP (1280×720 or 1920×1080)
├── DOM Snapshot: Accessibility tree extraction (simplified DOM)
│   ├── Element tag, type, role, text content
│   ├── Bounding box (x, y, width, height)
│   ├── Visibility status
│   └── Input attributes (type, autocomplete, name, id)
└── Output: (screenshot_image, dom_tree_json)

STAGE 3: LOCAL PERCEPTION
├── Input: screenshot + optional DOM context
├── Model: Qwen3.5-4B via llama.cpp server
├── Prompt: "Describe the UI elements visible. What is the current page state?"
├── Output: Structured understanding of the page
└── Latency target: < 500ms

STAGE 4: GROUNDING
├── Input: screenshot + task instruction + perceived elements
├── Model: Same VLM with grounding prompt
├── Prompt: "Where is the [target element]? Return bounding box coordinates."
├── Output: {element: "Search button", bbox: [x, y, w, h], confidence: 0.95}
├── Fallback: Use DOM bounding boxes if VLM grounding is uncertain
└── Latency target: < 300ms (can be combined with perception)

STAGE 5: PRIVACY DETECTION
├── Layer 1: DOM Scanner (instant, ~5ms)
│   ├── input[type=password] → SENSITIVE
│   ├── input[type=email] → SENSITIVE  
│   ├── autocomplete="cc-number" → SENSITIVE
│   ├── name/id containing "aadhaar", "pan", "ssn" → SENSITIVE
│   └── Label text matching PII keywords → SENSITIVE
├── Layer 2: OCR + Regex (~50ms)
│   ├── Run lightweight OCR on screenshot
│   ├── Regex: Aadhaar (12-digit with Verhoeff), PAN (AAAAA0000A)
│   ├── Regex: Email, phone (+91...), credit card patterns
│   └── Context check: "PAN", "Aadhaar" keywords near matches
├── Layer 3: Face Detection (~30ms)
│   ├── MediaPipe BlazeFace on screenshot
│   └── Any detected face bounding boxes → SENSITIVE
└── Output: List of {region, type, confidence, source}

STAGE 6: REDACTION / MASKING
├── Input: Screenshot + list of sensitive regions
├── Operations:
│   ├── Password fields: Black rectangle overlay
│   ├── Email/phone text: Pixelation or solid color block
│   ├── Face regions: Gaussian blur (σ=20)
│   ├── ID numbers: Solid mask with placeholder text
│   └── DOM-detected inputs: Black fill matching element bounds
├── Output: sanitized_screenshot (safe to transmit)
├── Verification: Re-run detection on sanitized image → should find 0 PII
└── Latency target: < 100ms

STAGE 7: ROUTING DECISION
├── Input: Task complexity estimate + network status + local model confidence
├── Decision logic:
│   ├── IF task is simple action (click identified button) → LOCAL
│   ├── IF local model confidence > threshold → LOCAL  
│   ├── IF task requires multi-step planning → REMOTE
│   ├── IF network unavailable → LOCAL (degraded mode)
│   └── DEFAULT → REMOTE with sanitized screenshot
├── Output: {route: "local" | "remote", reason: "..."}
└── Important: Remote path ONLY receives sanitized_screenshot

STAGE 8a: LOCAL ACTION (fast path)
├── Local VLM generates action directly
├── Prompt: "Given this UI state and task, what is the next action?"
├── Output: {action: "click", target: [x, y]} or {action: "type", text: "..."}
└── Latency: < 500ms total

STAGE 8b: REMOTE REASONING (complex path)  
├── Send: sanitized_screenshot + DOM summary + task + conversation history
├── Remote model: Qwen3.8-Max / GPT-4o / Gemini (via API)
├── Remote model reasons over sanitized screen
├── Output: {action: "click", target: "Submit button", reasoning: "..."}
├── Local agent maps "Submit button" to coordinates using local grounding
└── Latency: 1–5s (network dependent)

STAGE 9: ACTION COMMAND PARSING
├── Input: Raw model output (local or remote)
├── Parse into structured action:
│   ├── click(x, y)
│   ├── type(text, element_selector)
│   ├── scroll(direction, amount)
│   ├── navigate(url)
│   ├── select(option, element)
│   ├── wait(seconds)
│   └── done(summary)
└── Validate: Are coordinates within viewport? Is the action safe?

STAGE 10: BROWSER EXECUTION
├── Playwright executes the parsed action
├── click → page.mouse.click(x, y)
├── type → page.keyboard.type(text)
├── scroll → page.mouse.wheel(dx, dy)
├── navigate → page.goto(url)
├── Wait for page stability (network idle, DOM settled)
└── Latency: 100–500ms depending on page response

STAGE 11: VERIFICATION
├── Take new screenshot after action
├── Compare with expected outcome:
│   ├── Did the page change?
│   ├── Did the target element respond?
│   ├── Are we on the expected next page?
│   └── Did an error message appear?
├── If action failed → retry with different approach
├── If max retries exceeded → report failure
└── If task complete → return success + summary

STAGE 12: NEXT AGENT LOOP
├── If task not complete → GOTO STAGE 2
├── Carry forward:
│   ├── Conversation history (what actions were taken)
│   ├── Current task progress
│   ├── Error/retry count
│   └── Accumulated latency metrics
├── Safety: Max 20 iterations per task
└── Timeout: 120 seconds total task time
```

---

## KEY INSIGHT FOR JURY

> "Our system treats the browser like a human does — by looking at it. But unlike a human, it systematically detects and removes all sensitive information before any data leaves the device. The local model handles routine perception. The remote model only ever sees a sanitized version of reality."

This single sentence encapsulates our entire PS solution.
