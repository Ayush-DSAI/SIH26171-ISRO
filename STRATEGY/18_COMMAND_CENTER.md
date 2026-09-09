# PART 18 — FINAL TEAM COMMAND CENTER

---

## A. MASTER TEAM TABLE

| Member | Role | Subsystem | Technologies | Key Concepts | Mini-Project | Integration Task | Deadline | Backup | Jury Topics |
|--------|------|-----------|-------------|-------------|-------------|-----------------|----------|--------|-------------|
| **Ayush** | System Integrator + Agent UI | Agent loop, Action executor, Demo UI | Playwright, FastAPI, WebSocket, httpx | Agent loop, routing, grounding integration, action parsing | Agent loop with mock VLM | Connect all modules into working pipeline | Day 12 (MVP v0) | Shaurya | Agent loop, routing, architecture overview, demo walkthrough |
| **Shaurya** | Infrastructure + Model Lead | VLM server, Remote API, Verification | llama.cpp, GGUF, nvidia-smi, httpx, OpenCV | Quantization, VRAM, inference optimization, image similarity | VLM benchmarking tool | Optimize latency, remote client, verification module | Day 8 (server), Day 15 (remote) | Ayush | Quantization, VRAM, latency, model selection, inference pipeline |
| **Himanshu** | Networking + API + Docs | Routing, Privacy gateway, Telemetry, Docs | FastAPI, Pydantic, logging, Mermaid | API design, data flow, security, structured logging | Privacy gateway + telemetry | Wrap agent in API, privacy middleware, architecture diagrams | Day 10 (API), Day 20 (diagrams) | Aditi | Privacy architecture, API design, data flow, security model |
| **Aditi** | ML/VLM Research + Grounding | VLM perception, Grounding, OCR | HuggingFace, llama-server API, OpenCV, Jupyter | VLM architecture, visual grounding, prompt engineering, IoU | Grounding module | Optimize prompts, evaluate accuracy, DOM fallback | Day 9 (grounding), Day 14 (accuracy) | Shaurya | VLM architecture, grounding, quantization effects, model evaluation |
| **Abhishek** | Privacy + Redaction + Testing | PII detection, Face detection, Redaction, Benchmarks | regex, MediaPipe, OpenCV, Pillow, pytest | PII formats, Verhoeff, Luhn, precision/recall, masking | PII detection + redaction engine | Benchmark suite, edge cases, test coverage | Day 8 (engine), Day 25 (benchmarks) | Himanshu | PII detection, redaction, Verhoeff, benchmarks, false negative analysis |
| **Nidhi** | QA + Documentation + Demo | Test pages, Scenario matrix, Docs, Demo script | HTML/CSS, Markdown, GitHub Issues | System overview, test design, demo narration | Test suite + documentation | Collect results, format benchmarks, rehearse demo | Day 8 (test pages), Day 28 (PPT) | Himanshu | System overview, demo narration, test coverage, high-level privacy |

---

## B. MASTER ROADMAP

```
WEEK 1 (Days 1-7): FOUNDATION
├─ Day 1-2: Environment setup (ALL)
│  └─ llama-server running (SHAURYA — CRITICAL PATH)
├─ Day 3-4: Level 0+1 learning complete (ALL)
│  └─ First VLM inference test (SHAURYA + ADITI)
├─ Day 5-7: Mini-projects begin (ALL, parallel)
│  └─ Integration checkpoint: Day 7 team call

WEEK 2 (Days 8-14): PROTOTYPES + INITIAL INTEGRATION
├─ Day 8: Mini-projects complete (ALL)
│  └─ Each member demos their standalone module
├─ Day 9-11: Integration begins
│  ├─ Ayush + Shaurya: Agent loop → VLM server
│  ├─ Ayush + Aditi: Agent loop → Grounding module
│  └─ Ayush + Abhishek: Agent loop → Redaction engine
├─ Day 12: MVP v0 checkpoint
│  └─ Agent performs one task on test page

WEEK 3 (Days 15-21): HYBRID + FEATURES
├─ Day 15-17: Remote model integration
│  ├─ Shaurya: Remote API client
│  ├─ Himanshu: Privacy gateway wrapping outbound calls
│  └─ Ayush: Routing logic (local vs remote)
├─ Day 17: MVP v1 checkpoint
│  └─ Full hybrid pipeline: perception → redaction → routing → action
├─ Day 18-21: Polish
│  ├─ Demo UI (Ayush)
│  ├─ Edge case redaction (Abhishek)
│  └─ Architecture diagrams (Himanshu)

WEEK 4 (Days 22-28): BENCHMARKS + DEMO PREP
├─ Day 22-25: Benchmark execution
│  ├─ Abhishek: PII benchmark suite
│  ├─ Aditi: Grounding accuracy evaluation
│  ├─ Shaurya: Latency + VRAM profiling
│  └─ Nidhi: Results collection and formatting
├─ Day 25: MVP v2 checkpoint
│  └─ All benchmarks have numbers
├─ Day 26-28: Demo preparation
│  ├─ Himanshu + Nidhi: PPT creation
│  ├─ Nidhi: Demo script finalization
│  └─ All: First demo rehearsal

WEEK 5+ (Days 29-32): FINAL PREPARATION
├─ Day 29: Full demo rehearsal #2
├─ Day 30: Jury Q&A practice session
├─ Day 31: Final bug fixes, stress test
├─ Day 32: SIH PRESENTATION
│  └─ Demo rehearsal #3 (morning)
│  └─ PRESENT (scheduled time)
```

---

## C. DAILY/WEEKLY CHECKLIST

### Daily (Each Member)
- [ ] Pull latest from `dev` branch
- [ ] Complete assigned tasks for the day
- [ ] Push work to feature branch
- [ ] Post standup update in WhatsApp group (3 lines: done, doing, blocked)

### Weekly (Team)
- [ ] 30-minute sync call (ideally Sunday evening)
- [ ] Integration test: run full system
- [ ] Update GitHub Issues board
- [ ] Review milestone progress
- [ ] Identify and resolve blockers

---

## D. GITHUB TASK BOARD STRUCTURE

### Columns
| To Do | In Progress | Review | Done |

### Labels
| Label | Meaning |
|-------|---------|
| `critical-path` | Blocking other work |
| `module:agent` | Agent loop related |
| `module:perception` | VLM/grounding related |
| `module:privacy` | PII/redaction related |
| `module:server` | API/networking related |
| `module:infra` | Model serving/deployment |
| `module:docs` | Documentation/presentation |
| `module:test` | Testing/benchmarking |
| `bug` | Something is broken |
| `enhancement` | Improvement to existing feature |

### Milestones
| Milestone | Target Date | Criteria |
|-----------|------------|----------|
| M1: Environment Ready | Day 4 | All members have working environment |
| M2: Mini-Projects | Day 8 | 6 standalone prototypes |
| M3: MVP v0 | Day 12 | Agent loop works end-to-end |
| M4: MVP v1 | Day 17 | Hybrid pipeline with redaction |
| M5: MVP v2 | Day 25 | Benchmarks complete |
| M6: Demo Ready | Day 30 | Rehearsed demo, PPT done |
| **M7: SIH Day** | Day 32 | Present and win |

---

## E. DEPENDENCY GRAPH

```
                          ┌──────────────────────┐
                          │  Shaurya: llama-server│ ◄── CRITICAL START
                          │  (Day 1-3)            │
                          └──────────┬─────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                 │
          ┌─────────▼──────┐  ┌─────▼──────────┐     │
          │ Aditi: Grounding│  │ Shaurya: VLM   │     │
          │ (Day 5-9)      │  │ Benchmarks     │     │
          └─────────┬──────┘  │ (Day 5-8)      │     │
                    │         └────────────────┘     │
                    │                                 │
          ┌─────────▼────────────────────────────────▼──────┐
          │           Ayush: Agent Loop Integration          │
          │           (Day 9-12) → MVP v0                    │
          └─────────┬───────────────────┬───────────────────┘
                    │                   │
          ┌─────────▼──────┐  ┌────────▼───────────┐
          │ Abhishek:       │  │ Himanshu:          │
          │ Redaction into  │  │ API + Privacy      │
          │ loop (Day 12-15)│  │ Gateway (Day 12-16)│
          └─────────┬──────┘  └────────┬───────────┘
                    │                   │
          ┌─────────▼───────────────────▼───────────────────┐
          │           MVP v1: Hybrid Pipeline (Day 17)       │
          └─────────┬───────────────────────────────────────┘
                    │
          ┌─────────▼───────────────────────────────────────┐
          │ Benchmarks + Polish + Demo Prep (Day 18-30)      │
          │ Abhishek: benchmarks  │  Nidhi: results + PPT  │
          │ Aditi: grounding eval │  Himanshu: diagrams     │
          │ Shaurya: optimization │  Ayush: demo UI polish  │
          └─────────────────────────────────────────────────┘
```

---

## F. CRITICAL PATH (Blockers in Bold)

1. **Shaurya gets llama-server running with VLM (Day 1-3)** ← If this fails, use Ollama
2. **Aditi tests first grounding prompt (Day 5-6)** ← Needs Shaurya's server
3. Abhishek builds redaction engine (Day 5-8) ← Independent
4. **Ayush integrates VLM into agent loop (Day 9-11)** ← Needs Shaurya + Aditi
5. **Ayush adds redaction to loop (Day 12)** ← Needs Abhishek
6. Shaurya + Himanshu add remote API path (Day 13-16) ← Needs running loop
7. **MVP v1 demo (Day 17)** ← First full hybrid demo
8. Benchmarks (Day 22-25) ← Needs MVP v1
9. **Demo rehearsal (Day 29)** ← Needs benchmarks + PPT
10. **SIH Presentation (Day 32)**

---

## G. MVP DEFINITION (Summary)

| Version | Core Feature | Date |
|---------|-------------|------|
| **MVP v0** | Agent loop + VLM → one page, one action | Day 12 |
| **MVP v1** | + Redaction + hybrid routing | Day 17 |
| **MVP v2** | + Benchmarks + edge cases + polished UI | Day 25 |
| **Final** | + PPT + demo rehearsed + jury ready | Day 30 |

---

## H. FINAL DEMO DEFINITION

**Duration:** 4 minutes
**Structure:** Problem → Baseline → Our Solution (live redaction) → Hybrid reasoning → Metrics → Architecture → Close
**Key visual:** 3-panel view: Original | Detected | Sanitized
**Must show:** Live inference, real metrics, before/after screenshots, VRAM usage

---

## I. BENCHMARK PLAN (Summary)

| Benchmark | Owner | By Date |
|-----------|-------|---------|
| PII detection P/R/F1 | Abhishek | Day 24 |
| Grounding IoU | Aditi | Day 24 |
| Latency per stage | Shaurya + Abhishek | Day 23 |
| VRAM profiling | Shaurya | Day 23 |
| Baseline comparison | Abhishek + Aditi | Day 25 |
| Redaction completeness | Abhishek | Day 24 |
| Results formatting | Nidhi | Day 26 |

---

## J. JURY PREPARATION PLAN

| Activity | When | Who |
|----------|------|-----|
| Read all jury questions + answers | Day 26 | All |
| Practice Q&A (mock jury) | Day 28 | All |
| Practice demo narration | Day 28-29 | Nidhi (primary narrator) |
| Review architecture diagrams | Day 28 | Himanshu presents, all review |
| Final Q&A drill | Day 30 | All |
| Day-of warm-up Q&A | Day 32 (morning) | All |

---

## FINAL CHECKLIST (DAY OF SIH)

- [ ] Laptop charged + charger packed
- [ ] Internet connectivity tested (hotspot backup)
- [ ] llama-server pre-warmed (first inference done 10 min before demo)
- [ ] Demo test pages loaded in browser
- [ ] Demo UI open and connected via WebSocket
- [ ] Remote API key configured and tested
- [ ] Backup demo video on USB drive
- [ ] PPT on USB drive + cloud backup
- [ ] Each person knows their jury topics
- [ ] Timer visible during demo
- [ ] Deep breath. We've prepared. Execute.

---

> **"The team that wins SIH is not the team with the most features. It's the team that proves their core claim with measurable evidence, handles jury questions with confidence, and delivers a demo that the judges remember."**
>
> Ship the working system. Measure everything. Present with conviction.
