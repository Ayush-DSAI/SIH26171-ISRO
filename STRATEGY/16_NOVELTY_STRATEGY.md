# PART 16 — NOVELTY AND SIH COMPETITIVE STRATEGY

---

## LANDSCAPE ANALYSIS

### What Is Obvious/Common (Most Teams Will Do This)
1. Use a cloud model API (GPT-4o / Gemini) to "understand" screenshots
2. Use Selenium for browser automation
3. Claim "privacy" without measurable evidence
4. Build a simple form-filling demo
5. Use hardcoded selectors instead of visual perception
6. Show a single happy-path demo

### What Is Technically Challenging (Few Teams Will Solve This Well)
1. **Reliable PII detection** across DOM, rendered text, and images — with measured accuracy
2. **Visual grounding** that works on arbitrary unseen websites
3. **Post-redaction verification** proving completeness
4. **VRAM budget management** fitting everything in 8 GB
5. **Agent loop self-correction** when actions fail
6. **Hybrid routing** with graceful degradation

### What Can Be Our Novelty
1. **"Privacy by Architecture"** — not just a claim; an architectural guarantee with defense-in-depth
2. **Multi-layer detection** (DOM + Regex + Face + Verification) — catches what any single technique misses
3. **Post-redaction verification loop** — a unique safety mechanism
4. **Measured privacy** — we report precision, recall, F1 for PII detection, not just "we protect privacy"
5. **DOM + Vision fusion** — exploiting both structured data and visual understanding
6. **Graceful degradation** — system works (with reduced capability) even when cloud is unavailable
7. **Indian PII specialization** — Aadhaar (with Verhoeff), PAN, +91 phone patterns — not generic Western PII

---

## FEATURE RANKING

### 🔴 MUST HAVE (Without these, we don't have a valid solution)
| Feature | Why |
|---------|-----|
| Local VLM inference within 8 GB VRAM | Core PS constraint |
| Visual perception of webpages (screenshot → understanding) | Core PS requirement |
| UI element grounding (description → coordinates) | Required for agent action |
| DOM extraction for PII attribute detection | Cheapest, most reliable PII signal |
| Regex PII detection (Aadhaar, PAN, email, phone) | Indian-specific PII |
| Face detection | Visual PII that DOM can't catch |
| Screenshot redaction (mask/blur) | Privacy-preserving output |
| Agent loop (observe → act → verify) | Core agent functionality |
| Sanitized-only transmission to remote model | Hybrid privacy guarantee |
| Benchmark results (accuracy, latency, VRAM) | Evidence for claims |

### 🟡 SHOULD HAVE (Significantly strengthens the submission)
| Feature | Why |
|---------|-----|
| Post-redaction verification (re-scan sanitized image) | Unique safety mechanism |
| Local/remote routing with fallback | Demonstrates architectural sophistication |
| Real-time demo UI (3-panel: original/detected/sanitized) | Visually compelling demo |
| Latency breakdown dashboard | Engineering credibility |
| Privacy gateway middleware | Architectural enforcement |
| Multi-step task execution | Shows agent competence |
| Baseline comparison table (cloud-only vs local-only vs hybrid) | Puts our solution in context |

### 🟢 NICE TO HAVE (If time permits, adds polish)
| Feature | Why |
|---------|-----|
| GLiNER NER for names/addresses | Catches unstructured PII |
| PaddleOCR for better text extraction | Improves PII-in-image detection |
| Set-of-Mark prompting | Advanced grounding technique |
| Wireshark proof of no PII on wire | Dramatic security demo |
| Multi-website demo (3+ sites) | Shows generalization |
| Dark mode handling | Edge case robustness |
| Browser fallback (Playwright → CDP) | Engineering resilience |

### ❌ DO NOT BUILD (Overengineering that wastes time)
| Feature | Why Not |
|---------|---------|
| Custom VLM fine-tuning | No time, no data, pre-trained models are sufficient |
| Full database with user management | Unnecessary for prototype — JSON files suffice |
| Docker/Kubernetes deployment | Overkill for hackathon demo |
| Mobile/tablet support | Out of PS scope |
| Multi-language UI | Out of PS scope |
| Blockchain-based audit trail | Buzzword engineering, no technical value |
| Custom CAPTCHA solver | Ethically questionable, out of scope |
| Distributed model inference | One GPU is fine for our models |
| Voice/speech interface | Out of PS scope |
| Integration with ISRO internal systems | We don't have access; not expected |

---

## WHAT WOULD MAKE THE DEMO MEMORABLE

1. **The "privacy reveal"** — Side-by-side original vs sanitized screenshot. The moment judges SEE passwords and Aadhaar numbers disappear is worth 10 minutes of explanation.

2. **Live metrics** — Real-time inference time, VRAM usage, PII detection count ticking up. Shows engineering, not just a polished video.

3. **The blocked request** — Show the privacy gateway intercepting a hypothetical unredacted request. "This is what our system prevents."

4. **Aadhaar Verhoeff validation** — "We don't just match 12 digits — we validate the Verhoeff checksum. This random 12-digit number FAILS the check." ISRO evaluators will appreciate this specificity.

5. **Fallback demo** — Pull the internet cable. Agent switches to local-only mode. "Even without connectivity, privacy is preserved and the agent continues working."

6. **Benchmark table, not claims** — Put a clean table with precision, recall, latency, VRAM numbers on screen. Read a number aloud. "99.1% recall. Out of 100 sensitive fields, we catch 99."

---

## CLAIMS THAT MUST BE SUPPORTED BY EVIDENCE

| Claim | Required Evidence |
|-------|------------------|
| "Privacy-preserving" | PII detection recall benchmark (must be > 95%) |
| "Lightweight" | VRAM usage chart showing < 8 GB |
| "On-device" | System running on a consumer GPU, no cloud for perception |
| "Low latency" | Per-stage latency measurements with min/avg/max |
| "Accurate grounding" | IoU scores on test set |
| "Works on arbitrary websites" | Demo on 2-3 unseen websites |
| "Hybrid architecture" | Show both local and remote paths executing |
| "Fallback capable" | Demo working without internet connection |

**Rule: If we can't measure it, we don't claim it.**

---

## COMPETITIVE POSITIONING STATEMENT

> "Most solutions to this PS will use cloud APIs with raw screenshots. We are the team that makes privacy measurable. Our multi-layer detection achieves 98%+ recall, our architecture guarantees zero raw PII transmission, and our system runs entirely within 8 GB VRAM. We don't just claim privacy — we benchmark it."
