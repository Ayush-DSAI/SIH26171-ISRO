# PART 13 — TEAM WORKFLOW (Phase-by-Phase Execution Plan)

---

## PHASE OVERVIEW

| Phase | Duration | Focus | Exit Criteria |
|-------|----------|-------|---------------|
| **Phase 1** | Days 1–4 | Research + Environment Setup | Everyone has environment working, concepts understood |
| **Phase 2** | Days 5–8 | Independent Mini-Projects | 6 standalone prototypes working |
| **Phase 3** | Days 9–12 | Subsystem Integration | MVP v0 — agent loop working end-to-end |
| **Phase 4** | Days 13–17 | Hybrid Architecture | MVP v1 — perception + redaction + routing working |
| **Phase 5** | Days 18–22 | Optimization + Polish | MVP v2 — hybrid path working, edge cases handled |
| **Phase 6** | Days 23–27 | Benchmarking + Testing | All benchmarks complete, results documented |
| **Phase 7** | Days 28–32 | Demo + PPT + Jury Prep | Rehearsed demo, final PPT, jury Q&A ready |

---

## PHASE 1: RESEARCH + ENVIRONMENT SETUP (Days 1–4)

### Who Works With Whom
| Pair | Activity |
|------|----------|
| Shaurya + Aditi | Set up llama-server, download models, first VLM inference test |
| Ayush + Himanshu | Set up project repo, Playwright installation, FastAPI skeleton |
| Abhishek + Nidhi | Install MediaPipe/OpenCV, learn regex, create first test page |

### Deliverables
- [ ] GitHub repo created with directory structure (Ayush)
- [ ] Everyone has Python environment + dependencies installed (All)
- [ ] llama-server running with Qwen3.5-4B on Shaurya's machine (Shaurya)
- [ ] First successful VLM inference with a screenshot (Shaurya + Aditi)
- [ ] Playwright installed and can take a screenshot (Ayush)
- [ ] MediaPipe face detection working on a test image (Abhishek)
- [ ] First test HTML page created (Nidhi)
- [ ] Everyone has completed their Level 0 + Level 1 learning (All)

### Integration Checkpoint
**Day 4 team meeting:** Everyone demos their working environment. Shaurya shows the VLM responding to an image prompt.

---

## PHASE 2: INDEPENDENT MINI-PROJECTS (Days 5–8)

### Who Does What (Parallel — No Dependencies)
| Member | Mini-Project | Works Alone/With |
|--------|-------------|-----------------|
| Ayush | Agent loop with mock VLM | Alone |
| Shaurya | VLM benchmarking (latency × quantization) | Alone (Aditi consults) |
| Aditi | Grounding module (screenshot + description → bbox) | Uses Shaurya's server |
| Abhishek | PII detection + redaction engine | Alone |
| Himanshu | Privacy gateway + telemetry middleware | Alone |
| Nidhi | 10 test pages + scenario matrix + docs | Alone (Abhishek consults for PII formats) |

### Deliverables
- [ ] 6 standalone mini-project folders with README, src, tests, results (All)
- [ ] Each mini-project has a documented interface (input/output format) (All)

### Integration Checkpoint
**Day 8 team meeting:** Each member demos their mini-project. Define interface contracts for integration.

---

## PHASE 3: SUBSYSTEM INTEGRATION (Days 9–12)

### Who Works With Whom
| Integration | Members | What Happens |
|-------------|---------|-------------|
| Agent Loop + VLM | Ayush + Shaurya | Replace mock VLM with real llama-server calls |
| Agent Loop + Grounding | Ayush + Aditi | Agent uses grounding module to locate elements |
| Agent Loop + Redaction | Ayush + Abhishek | Agent calls redaction before outbound requests |
| API + Agent | Ayush + Himanshu | Wrap agent in FastAPI endpoints + WebSocket |
| Tests + Redaction | Abhishek + Nidhi | Run redaction engine on all 10 test pages |
| Telemetry + All | Himanshu | Hook timing collection into all modules |

### Deliverables
- [ ] Agent loop takes a screenshot → sends to VLM → gets action → executes (Ayush + Shaurya)
- [ ] Grounding works in the loop (click identified elements) (Ayush + Aditi)
- [ ] Redaction runs on screenshot before any remote call (Ayush + Abhishek)
- [ ] FastAPI serves the agent, WebSocket streams status (Ayush + Himanshu)
- [ ] 10 test pages evaluated with redaction results (Abhishek + Nidhi)

### Integration Checkpoint
**Day 12:** MVP v0 — Live demo of agent performing a simple task on a test page. VLM describes the page, agent clicks a button, verifies success.

---

## PHASE 4: HYBRID ARCHITECTURE (Days 13–17)

### Who Works With Whom
| Task | Members | What Happens |
|------|---------|-------------|
| Routing logic | Ayush | Implement local vs remote decision function |
| Remote model client | Shaurya + Himanshu | Call cloud API with sanitized screenshots |
| Privacy gateway integration | Himanshu | Validate outbound requests go through privacy check |
| Multi-step tasks | Ayush + Aditi | Agent handles 3+ step tasks (e.g., "search and click result") |
| OCR + regex layer | Aditi + Abhishek | Connect OCR output to PII regex scanner |
| Demo UI | Ayush + Nidhi | Build real-time dashboard with panels |

### Deliverables
- [ ] Agent routes simple tasks locally, complex tasks remotely (Ayush)
- [ ] Remote model receives ONLY sanitized screenshots (Shaurya + Himanshu)
- [ ] Privacy gateway blocks any request with detected PII (Himanshu)
- [ ] Multi-step task working (Ayush + Aditi)
- [ ] Demo UI showing original/detected/sanitized panels (Ayush)

### Integration Checkpoint
**Day 17:** MVP v1 — Full hybrid pipeline working. Demo the 3-panel redaction view. Show routing decision in logs.

---

## PHASE 5: OPTIMIZATION + POLISH (Days 18–22)

### Who Works on What
| Task | Member | Target |
|------|--------|--------|
| Inference speed optimization | Shaurya | < 500ms local inference |
| Prompt optimization | Aditi | Best accuracy prompt found |
| Redaction edge cases | Abhishek | Handle: dark mode, images, shadow DOM |
| Fallback mode (no internet) | Ayush | Agent works in local-only mode |
| Architecture diagrams | Himanshu | 4+ professional diagrams |
| Additional test pages | Nidhi | Add edge case pages |
| Demo UI polish | Ayush | Animations, layout, colors |

### Deliverables
- [ ] Inference consistently < 500ms (Shaurya)
- [ ] Edge case redaction tested: dark mode, face angles, image PII (Abhishek)
- [ ] Fallback mode works when remote API is unavailable (Ayush)
- [ ] Professional architecture diagrams ready (Himanshu)
- [ ] Demo UI is visually impressive (Ayush)

---

## PHASE 6: BENCHMARKING + TESTING (Days 23–27)

### Who Works on What
| Task | Member |
|------|--------|
| Full benchmark suite execution | Abhishek |
| Grounding accuracy evaluation | Aditi |
| VRAM profiling | Shaurya |
| Benchmark results formatting | Nidhi |
| Privacy validation report | Himanshu |
| Integration testing, bug fixes | Ayush |

### Deliverables
- [ ] PII detection: precision, recall, F1 per type (Abhishek)
- [ ] Grounding: IoU per element type (Aditi)
- [ ] Latency: per-module breakdown (Abhishek + Shaurya)
- [ ] VRAM: component-by-component usage (Shaurya)
- [ ] Baseline comparison table (Abhishek + Aditi)
- [ ] Results formatted into presentation-ready charts (Nidhi)
- [ ] Privacy audit log proving no PII leakage (Himanshu)

---

## PHASE 7: DEMO + PPT + JURY PREPARATION (Days 28–32)

### Who Works on What
| Task | Member |
|------|--------|
| Final demo rehearsal (5+ runs) | All |
| PPT creation | Himanshu + Nidhi |
| Jury Q&A practice | All |
| Backup video recording | Nidhi |
| System stress testing | Shaurya + Ayush |
| Last-minute bug fixes | Ayush + Abhishek |

### Deliverables
- [ ] Demo runs 5 times without failure (All)
- [ ] PPT complete with architecture, benchmarks, results (Himanshu + Nidhi)
- [ ] Each member can answer their jury topics (All)
- [ ] Backup demo video recorded (Nidhi)
- [ ] README finalized with setup instructions (Nidhi + Himanshu)

---

## CRITICAL PATH

```
Shaurya: llama-server working (Day 3)
         ↓
Aditi: First grounding test (Day 6)
         ↓
Ayush: Agent loop with real VLM (Day 10)
         ↓
Abhishek: Redaction integrated into loop (Day 12)
         ↓
Ayush + Shaurya: Hybrid path working (Day 16)
         ↓
All: Benchmarks complete (Day 26)
         ↓
All: Demo rehearsed (Day 30)
```

**If Shaurya's llama-server is delayed → EVERYTHING is delayed.** This is the #1 priority.

**Fallback:** If llama-server fails, use Ollama (simpler setup, same models). If Ollama fails, use Hugging Face Transformers directly (more VRAM, slower, but guaranteed to work).

---

## DAILY STANDUP FORMAT (10 minutes)

Every team member answers:
1. What did I complete yesterday?
2. What am I working on today?
3. Am I blocked on anything?

**Communication tool:** WhatsApp group + GitHub Issues

**Weekly deep sync (30 min):** Full integration check. Everyone runs the combined system. Identify gaps.

---

## BUILD FIRST PRIORITY ORDER

1. **llama-server with VLM** (Shaurya) — Without this, no perception
2. **Screenshot + DOM extraction** (Ayush) — Without this, no observation
3. **Agent loop skeleton** (Ayush) — Orchestration backbone
4. **Grounding module** (Aditi) — Without this, no action
5. **PII detection** (Abhishek) — Without this, no privacy claim
6. **Redaction** (Abhishek) — Without this, no demo
7. **Remote API + routing** (Shaurya + Himanshu) — Hybrid path
8. **Demo UI** (Ayush) — Visual impact
9. **Benchmarks** (Abhishek) — Evidence
10. **PPT + docs** (Himanshu + Nidhi) — Jury presentation
