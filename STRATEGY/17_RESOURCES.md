# PART 17 — RESOURCES / LEARNING PLAN (Per Member)

---

## AYUSH — System Integration + Agent Interface

### Essential Resources
1. **Playwright Python Documentation** — https://playwright.dev/python/docs/intro
   - Focus: Page interactions, screenshots, accessibility tree, async API
   - *This is your primary tool. Read the "Getting Started" and "Pages" sections thoroughly.*

2. **FastAPI Tutorial** — https://fastapi.tiangolo.com/tutorial/
   - Focus: REST endpoints, WebSocket, middleware, Pydantic models
   - *Read through the first 10 tutorial pages. Then read the WebSocket section.*

3. **Browser-Use GitHub** — https://github.com/browser-use/browser-use
   - Study the agent loop architecture. You don't have to use it, but understand how they structure observe→think→act.
   - *Read the source code of the core Agent class.*

### Paper
- **"WebArena: A Realistic Web Environment for Building Autonomous Agents"** (2023, Zhou et al.)
  - Exactly our problem domain. Study the agent loop design and evaluation methodology.

### Practical Exercise
- Build a Playwright script that: opens Google → types "ISRO SIH 2026" → clicks search → takes screenshot → extracts all link texts from results. Do this in 30 minutes.

---

## SHAURYA — Backend + Model Infrastructure

### Essential Resources
1. **llama.cpp Documentation** — https://github.com/ggml-org/llama.cpp
   - Focus: `llama-server` flags, multimodal support (`--mmproj`), GPU layer offloading
   - *Build from source with CUDA. Run the multimodal examples.*

2. **GGUF Model Collection (ggml-org)** — https://huggingface.co/collections/ggml-org/multimodal-ggufs-68244e01ff1f39e5bebeeedc
   - Find Qwen3.5-4B GGUF files here. Understand Q4_K_M vs Q5_K_M.

3. **Qwen-VL Model Card** — https://huggingface.co/Qwen/Qwen3.5-4B-Instruct
   - Understand the model's capabilities, input format, and limitations.

4. **nvidia-smi Guide** — Search "nvidia-smi tutorial VRAM monitoring"
   - Learn to monitor VRAM usage in real-time.

### Paper
- **"Qwen-VL: A Versatile Vision-Language Model for Understanding, Localization, Text Reading, and Beyond"** (Bai et al.)
  - Understand the architecture you're deploying.

### Practical Exercise
- Download Qwen3.5-4B Q4_K_M. Start llama-server. Send a screenshot via curl and get a text response. Measure VRAM usage. Do this on Day 2.

---

## HIMANSHU — Networking + API + Architecture

### Essential Resources
1. **FastAPI Full Tutorial** — https://fastapi.tiangolo.com/tutorial/
   - Focus: Dependency injection, middleware, WebSocket, CORS, error handling
   - *Go deeper than Ayush. You're designing the API, not just using it.*

2. **RESTful API Design Best Practices** — Search "REST API design guide Microsoft" or Google API design guide
   - Understand resource naming, HTTP methods, error codes, pagination.

3. **Python Structured Logging** — https://docs.python.org/3/howto/logging.html
   - Focus: Custom formatters, JSON output, PII-safe logging patterns.

4. **Mermaid.js Diagram Syntax** — https://mermaid.js.org/intro/
   - Create architecture diagrams that render in GitHub markdown.

### Paper
- **"On the Security Risks of Knowledge Transfer from VLMs"** or any VLM security paper
  - Understand prompt injection and data leakage risks in multimodal systems.

### Practical Exercise
- Design the API specification (OpenAPI) for our agent server. Define 5 endpoints with request/response schemas. Create a Mermaid sequence diagram of the full agent flow.

---

## ADITI — ML/VLM Research + Grounding

### Essential Resources
1. **Qwen-VL Technical Blog/Paper** — https://qwen.ai (blog section)
   - Understand architecture: ViT vision encoder → projection → LLM decoder.
   - *Draw the architecture from memory after reading.*

2. **"Set-of-Mark Prompting for GPT-4V"** — Search "Set-of-Mark Visual Grounding"
   - Technique: overlay numbered labels on UI elements, ask model to identify by number.
   - *Implement this as a stretch goal.*

3. **Hugging Face VLM Course** — https://huggingface.co/learn (multimodal section)
   - Understand vision-language model fundamentals.

4. **OpenCV Bounding Box Tutorial** — Search "OpenCV draw bounding box Python"
   - Visualize grounding results on screenshots.

### Paper
- **"SeeClick: Harnessing GUI Grounding for Advanced Visual GUI Agents"** (Cheng et al., 2024)
  - Directly relevant: GUI element grounding for browser agents. Study their evaluation methodology.

### Practical Exercise
- Take 10 screenshots of different websites. For each, manually annotate 3 elements with bounding boxes. Then prompt the VLM to ground those elements. Calculate IoU. Produce a grounding accuracy report.

---

## ABHISHEK — Privacy + Redaction + Testing

### Essential Resources
1. **Python `re` Module Documentation** — https://docs.python.org/3/library/re.html
   - Master: compile, findall, sub, named groups, lookahead/lookbehind.
   - *You will write 10+ regex patterns. Know this module deeply.*

2. **MediaPipe Face Detection Guide** — https://ai.google.dev/edge/mediapipe/solutions/vision/face_detector/python
   - Setup, configuration, confidence thresholds, bounding box extraction.

3. **Verhoeff Algorithm** — Search "Verhoeff algorithm Python implementation"
   - Implement from scratch. Understand the dihedral group D5 and check digit calculation.
   - *Required for Aadhaar validation.*

4. **OpenCV Image Manipulation** — Search "OpenCV rectangle blur mask Python"
   - Drawing rectangles, Gaussian blur, region masking.

### Paper
- **"Presidio: Context-Aware, Pluggable PII Detection and Anonymization"** (Microsoft)
  - Study their PII detection architecture. We're building a lightweight version.

### Practical Exercise
- Create `pii_patterns.py`: Implement regex + validation for Aadhaar (with Verhoeff), PAN, email, phone, credit card (with Luhn). Write 50 test cases (25 positive, 25 negative). Achieve 100% accuracy.

---

## NIDHI — QA + Documentation + Demo

### Essential Resources
1. **HTML Forms Tutorial** — https://developer.mozilla.org/en-US/docs/Learn/Forms
   - Learn: input types, form attributes, autocomplete values.
   - *You need to create realistic test pages with diverse form elements.*

2. **Markdown Guide** — https://www.markdownguide.org/basic-syntax/
   - Tables, code blocks, headers, links. You'll write lots of documentation.

3. **GitHub Issues Guide** — https://docs.github.com/en/issues/tracking-your-work-with-issues
   - Create issues, assign, label, milestones, boards.

4. **SIH Presentation Guidelines** — Check sih.gov.in for any official presentation format/time requirements.

### Paper
- **No paper required.** Instead, read the project's `01_PROBLEM_UNDERSTANDING.md` and `02_REFERENCE_ARCHITECTURE.md` thoroughly. Be able to explain the system in your own words.

### Practical Exercise
- Create 3 HTML pages (login form, profile page, payment form) with realistic fake PII. Open them in a browser and manually identify every PII element. Write a test scenario matrix for each page.

---

## RESOURCE VERIFICATION NOTE

All recommended resources are:
- **Official documentation** (Playwright, FastAPI, Python, MediaPipe, OpenCV) — stable, maintained
- **Major open-source repositories** (llama.cpp, browser-use) — active, widely used
- **Academic papers** — published and peer-reviewed
- **Hugging Face model cards** — official model documentation
- **No random YouTube tutorials** — focus on primary sources

If any resource link is broken, search for the title on the official website or Google Scholar.
