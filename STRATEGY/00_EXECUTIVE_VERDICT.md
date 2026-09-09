# EXECUTIVE VERDICT — SIH 2026: On-Device Visual Perception for Lightweight Browser Agents

## Date: September 8, 2026
## Organization: ISRO | PS Code: SIH26171

---

## ONE-LINE VERDICT

**Build a privacy-preserving hybrid browser agent that uses a local lightweight VLM (Qwen3.5-4B, ~3.5 GB VRAM) for visual perception and UI grounding, a local redaction engine for PII/face masking, and a remote large model (accessed only with sanitized screenshots) for complex reasoning — all orchestrated through a Playwright-based agent loop.**

---

## WHAT WE ARE BUILDING

A **browser automation agent** that:
1. **Sees** web pages through screenshots + DOM extraction
2. **Understands** UI elements using a lightweight on-device VLM
3. **Detects** sensitive information (passwords, emails, faces, Aadhaar, PAN) using DOM analysis + regex + face detection
4. **Redacts** all PII before any data leaves the device
5. **Routes** tasks: simple ones handled locally, complex ones sent (sanitized) to a remote model
6. **Executes** browser actions (click, type, scroll) based on model outputs
7. **Verifies** action success and loops until the task is complete

## WHY THIS WINS

| Dimension | Our Advantage |
|-----------|---------------|
| **Privacy** | Measurable, demonstrable — raw screenshots NEVER leave the device |
| **Efficiency** | Qwen3.5-4B @ Q4 runs in ~3.5 GB VRAM, leaving room for face detection + OCR |
| **Latency** | Local perception < 500ms, only complex reasoning hits the network |
| **Robustness** | DOM + Vision hybrid catches what either alone misses |
| **Demo Impact** | Side-by-side original vs. redacted screenshot is visually undeniable |
| **ISRO Alignment** | Privacy-first, resource-constrained, on-device — exactly their mandate |

## WINNING ARCHITECTURE (SUMMARY)

```
USER TASK (natural language)
        │
        ▼
┌─────────────────────────────────┐
│   BROWSER LAYER (Playwright)    │
│   - Navigate, click, type       │
│   - Screenshot capture          │
│   - DOM extraction              │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│   LOCAL PERCEPTION ENGINE       │
│   - Qwen3.5-4B (Q4_K_M GGUF)   │
│   - UI element grounding        │
│   - Scene understanding         │
│   - ~3.5 GB VRAM                │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│   PRIVACY / REDACTION ENGINE    │
│   - DOM attribute scanner       │
│   - Regex PII (Aadhaar/PAN/     │
│     email/phone)                │
│   - MediaPipe face detection    │
│   - OCR → regex pipeline        │
│   - Pixel-level masking         │
│   ~200 MB additional VRAM       │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│   ROUTING DECISION              │
│   - Complexity estimator        │
│   - Can local model handle it?  │
│   - Network available?          │
└─────┬───────────────┬───────────┘
      │               │
  LOCAL PATH      REMOTE PATH
      │               │
      ▼               ▼
┌───────────┐  ┌──────────────────┐
│ Local VLM │  │ Sanitized screen │
│ reasoning │  │ → Remote Model   │
│           │  │ (GPT-4o/Gemini/  │
│           │  │  Qwen3.8-Max)    │
└─────┬─────┘  └────────┬─────────┘
      │                  │
      └────────┬─────────┘
               │
               ▼
┌─────────────────────────────────┐
│   ACTION EXECUTOR               │
│   - Parse action command        │
│   - Execute via Playwright      │
│   - Click/type/scroll/navigate  │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│   VERIFICATION + LOOP           │
│   - Screenshot after action     │
│   - Compare expected vs actual  │
│   - Next iteration or done      │
└─────────────────────────────────┘
```

## TEAM ALLOCATION (SUMMARY)

| Member | Primary Role | Key Subsystem |
|--------|-------------|---------------|
| **Ayush** | System Integrator + Agent UI | Agent loop, demo UI, end-to-end pipeline |
| **Shaurya** | Infrastructure + Model Lead | Local inference server, quantization, remote API |
| **Himanshu** | Networking + API + Docs | Local↔remote comms, API design, architecture defense |
| **Aditi** | ML/VLM Research + Grounding | VLM selection, grounding accuracy, model evaluation |
| **Abhishek** | Privacy + Redaction + Benchmarks | PII detection, face blur, redaction engine, testing |
| **Nidhi** | QA + Documentation + Demo | Test scenarios, demo scripts, results collection, presentation |

## CRITICAL PATH

```
Week 1: Research + Setup → Everyone has environment running
Week 2: Independent mini-projects → 6 standalone prototypes
Week 3: Integration → Agent loop + perception + redaction connected
Week 4: Hybrid architecture → Remote reasoning path working
Week 5: Optimization → Latency tuning, edge cases, benchmarks
Week 6: Polish → Demo, benchmarks table, jury prep
Week 7: FINAL → Demo rehearsal, PPT, jury Q&A practice
```

## READ THE FULL STRATEGY

This document is Part 0 of 18. See the following files:

| File | Content |
|------|---------|
| `01_PROBLEM_UNDERSTANDING.md` | Deep PS analysis, pipeline explanation |
| `02_REFERENCE_ARCHITECTURE.md` | All 17 modules with specs |
| `03_TECH_STACK.md` | Complete stack with comparisons |
| `04_TEAM_ROLES.md` | Detailed role assignments |
| `05_LEARNING_CURRICULUMS.md` | Per-member L0–L5 curriculum |
| `06_MINI_PROJECTS.md` | 6 standalone mini-projects |
| `07_MVP_DEFINITION.md` | MVP v0 → Final demo |
| `08_WINNING_DEMO.md` | 3–5 minute demo script |
| `09_BENCHMARKING.md` | Metrics, experiments, baselines |
| `10_FAILURE_MODES.md` | 30+ failure modes + mitigations |
| `11_SECURITY_THREAT_MODEL.md` | Complete threat model |
| `12_REPO_ARCHITECTURE.md` | Git structure + workflows |
| `13_TEAM_WORKFLOW.md` | Phase-by-phase execution plan |
| `14_JURY_DEFENSE_MATRIX.md` | Who knows what matrix |
| `15_JURY_QUESTIONS.md` | 40+ questions with answers |
| `16_NOVELTY_STRATEGY.md` | Competitive differentiation |
| `17_RESOURCES.md` | Per-member learning resources |
| `18_COMMAND_CENTER.md` | Master tables + checklists |
