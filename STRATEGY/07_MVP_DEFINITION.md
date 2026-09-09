# PART 7 — MVP DEFINITION

---

## MVP v0 — "Proof of Concept" (End of Week 2)

**Goal:** Prove the agent loop works end-to-end on a SINGLE hardcoded scenario.

| Feature | Status | Owner |
|---------|--------|-------|
| Open a browser, navigate to a test page | ✅ | Ayush |
| Take screenshot + extract DOM | ✅ | Ayush |
| Send screenshot to local VLM | ✅ | Shaurya |
| VLM describes the page | ✅ | Aditi |
| Agent decides next action (click a button) | ✅ | Ayush |
| Execute the click | ✅ | Ayush |
| Verify action (new screenshot shows change) | ✅ | Shaurya |
| PII detection on test page | ❌ Not yet | — |
| Redaction | ❌ Not yet | — |
| Remote model | ❌ Not yet | — |
| Demo UI | ❌ Not yet | — |

**Sacrifice if time runs out:** Use Ollama instead of llama-server (easier setup). Use hardcoded action parsing (not flexible prompts).

**Estimated effort:** 5 person-days (Ayush 2, Shaurya 2, Aditi 1)

---

## MVP v1 — "Core Pipeline" (End of Week 3)

**Goal:** Perception + Redaction + Basic Privacy working together.

| Feature | Status | Owner |
|---------|--------|-------|
| Everything in MVP v0 | ✅ | — |
| VLM grounds specific UI elements (bounding boxes) | ✅ | Aditi |
| DOM-based PII detection (password/email fields) | ✅ | Abhishek |
| Regex PII detection (Aadhaar, PAN, phone, email in text) | ✅ | Abhishek |
| Face detection on screenshots | ✅ | Abhishek |
| Redaction engine (mask/blur sensitive regions) | ✅ | Abhishek |
| Before/after screenshot comparison | ✅ | Ayush |
| Basic privacy gateway (block raw PII in outbound requests) | ✅ | Himanshu |
| Simple demo page showing the pipeline | ✅ | Ayush + Nidhi |
| 5 test pages created | ✅ | Nidhi |

**Sacrifice if time runs out:** Drop face detection (keep it to DOM + regex only). Drop privacy gateway (manual validation instead).

**Estimated effort:** 12 person-days

---

## MVP v2 — "Hybrid Architecture" (End of Week 4)

**Goal:** Local → Redaction → Remote → Action — the full hybrid path working.

| Feature | Status | Owner |
|---------|--------|-------|
| Everything in MVP v1 | ✅ | — |
| Routing decision (local vs remote) | ✅ | Ayush |
| Send sanitized screenshot to remote model | ✅ | Shaurya + Himanshu |
| Remote model returns action command | ✅ | Shaurya |
| Agent executes remote-suggested actions | ✅ | Ayush |
| Post-redaction verification (re-scan sanitized image) | ✅ | Abhishek |
| Demo UI with real-time WebSocket updates | ✅ | Ayush |
| Latency metrics displayed in UI | ✅ | Himanshu |
| 10 test pages with full scenario matrix | ✅ | Nidhi |
| Multi-step task execution (3+ steps) | ✅ | Ayush + Aditi |

**Sacrifice if time runs out:** Use a simpler remote model (GPT-4o-mini instead of GPT-4o). Drop multi-step to single-step. Simplify routing to "always remote."

**Estimated effort:** 10 person-days

---

## Final Demo (End of Week 6)

**Goal:** Polished, visually compelling, benchmark-backed demo.

| Feature | Status | Owner |
|---------|--------|-------|
| Everything in MVP v2 | ✅ | — |
| Optimized inference (< 500ms local, < 3s remote) | ✅ | Shaurya |
| Comprehensive benchmarks (precision, recall, latency, VRAM) | ✅ | Abhishek |
| Fallback when remote server is unavailable | ✅ | Ayush |
| Edge case handling (modals, popups, dynamic content) | ✅ | Ayush + Aditi |
| Polished demo UI with animations, panels, metrics | ✅ | Ayush |
| Architecture diagrams and PPT | ✅ | Himanshu |
| Demo script rehearsed 3+ times | ✅ | Nidhi + all |
| Jury Q&A preparation complete | ✅ | All |

**Sacrifice if time runs out:** Cut edge case handling to 3 cases (instead of all). Skip the polished UI animations. Focus on WORKING demo + strong benchmarks.

---

## MVP DECISION RULES

**IF we are behind schedule:**
1. Cut UI polish FIRST (working > pretty)
2. Cut edge cases SECOND (happy path > robustness)
3. Cut remote model THIRD (local-only demo is still valid)
4. NEVER cut redaction (this IS our PS — without privacy, we have nothing)
5. NEVER cut benchmarks (claims without numbers = jury rejection)

**IF we are ahead of schedule:**
1. Add more test scenarios
2. Polish demo UI
3. Add GLiNER NER layer
4. Add benchmark comparisons vs baselines
5. Handle more edge cases (CAPTCHA detection, iframe handling)
