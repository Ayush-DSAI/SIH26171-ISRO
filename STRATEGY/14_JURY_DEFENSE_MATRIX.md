# PART 14 — JURY DEFENSE MATRIX

---

## KNOWLEDGE MATRIX

**Legend:**
- 🔴 **Must Know** — Can explain in detail, answer follow-up questions
- 🟡 **Should Know** — Understands the concept, can give a correct summary
- 🟢 **Nice to Know** — Aware of the concept, can point to the right person
- 👤 **Primary Responder** — This person answers first during jury Q&A

---

| Topic | Ayush | Shaurya | Himanshu | Aditi | Abhishek | Nidhi | Primary Responder |
|-------|-------|---------|----------|-------|----------|-------|-------------------|
| **VLM architecture** | 🟡 | 🟡 | 🟢 | 🔴 | 🟢 | 🟢 | 👤 Aditi |
| **Visual grounding** | 🟡 | 🟡 | 🟢 | 🔴 | 🟢 | 🟢 | 👤 Aditi |
| **OCR** | 🟡 | 🟢 | 🟢 | 🔴 | 🟡 | 🟢 | 👤 Aditi |
| **Browser automation (Playwright)** | 🔴 | 🟡 | 🟡 | 🟢 | 🟢 | 🟢 | 👤 Ayush |
| **DOM extraction** | 🔴 | 🟢 | 🟡 | 🟢 | 🟡 | 🟢 | 👤 Ayush |
| **PII redaction** | 🟡 | 🟢 | 🟡 | 🟢 | 🔴 | 🟡 | 👤 Abhishek |
| **PII detection (regex/DOM)** | 🟡 | 🟢 | 🟡 | 🟢 | 🔴 | 🟡 | 👤 Abhishek |
| **Privacy architecture** | 🟡 | 🟡 | 🔴 | 🟡 | 🟡 | 🟡 | 👤 Himanshu |
| **Latency analysis** | 🟡 | 🔴 | 🟡 | 🟢 | 🟡 | 🟢 | 👤 Shaurya |
| **Quantization (GGUF/Q4)** | 🟡 | 🔴 | 🟢 | 🟡 | 🟢 | 🟢 | 👤 Shaurya |
| **GPU/VRAM management** | 🟡 | 🔴 | 🟢 | 🟡 | 🟢 | 🟢 | 👤 Shaurya |
| **Local inference (llama.cpp)** | 🟡 | 🔴 | 🟢 | 🟡 | 🟢 | 🟢 | 👤 Shaurya |
| **Remote inference (API)** | 🟡 | 🔴 | 🟡 | 🟢 | 🟢 | 🟢 | 👤 Shaurya |
| **API design (REST/WS)** | 🟡 | 🟡 | 🔴 | 🟢 | 🟢 | 🟢 | 👤 Himanshu |
| **WebSocket** | 🟡 | 🟢 | 🔴 | 🟢 | 🟢 | 🟢 | 👤 Himanshu |
| **Agent loop** | 🔴 | 🟡 | 🟡 | 🟡 | 🟢 | 🟢 | 👤 Ayush |
| **Planner / task decomposition** | 🔴 | 🟡 | 🟢 | 🟡 | 🟢 | 🟢 | 👤 Ayush |
| **Tool / action execution** | 🔴 | 🟡 | 🟢 | 🟢 | 🟢 | 🟢 | 👤 Ayush |
| **Model hallucination** | 🟡 | 🟡 | 🟢 | 🔴 | 🟢 | 🟢 | 👤 Aditi |
| **Prompt injection** | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟢 | 👤 Himanshu |
| **Security model** | 🟡 | 🟡 | 🔴 | 🟢 | 🟡 | 🟢 | 👤 Himanshu |
| **Benchmarking methodology** | 🟡 | 🟡 | 🟢 | 🟡 | 🔴 | 🟡 | 👤 Abhishek |
| **Face detection** | 🟢 | 🟢 | 🟢 | 🟡 | 🔴 | 🟢 | 👤 Abhishek |
| **System overview** | 🔴 | 🔴 | 🔴 | 🟡 | 🟡 | 🟡 | 👤 Ayush or Himanshu |

---

## JURY Q&A PROTOCOL

### Before the Jury Session
1. Each member reviews their 🔴 and 🟡 topics for 30 minutes
2. Practice the most likely 10 questions as a team

### During the Jury Session
1. **Question comes in** → the Primary Responder takes it
2. If the question spans multiple topics → Primary Responder answers, others ADD details
3. If the Primary Responder is unsure → they say "Let me ask [Name] to elaborate on the [specific aspect]"
4. **NEVER** say "I don't know" without redirecting to a teammate
5. **ALWAYS** end technical answers with measurable evidence: "...and our benchmarks show X% accuracy"

### Emergency Protocol
If a question is completely unexpected:
1. Relate it to something you DO know: "That's an excellent question. In our architecture, the closest analog is..."
2. Be honest: "We haven't tested that specific scenario, but our fallback mechanism would..."
3. Never bluff — ISRO engineers will catch it

---

## COVERAGE ANALYSIS

**End-to-end system (can explain everything):** Ayush, Shaurya (2 people ✅)

**Deep ML/VLM expertise:** Aditi (primary), Shaurya (secondary) (2 people ✅)

**Privacy/security defense:** Himanshu (architecture), Abhishek (implementation) (2 people ✅)

**Demo narration:** Nidhi (primary), Himanshu (secondary) (2 people ✅)

**Benchmarks with evidence:** Abhishek (primary), Shaurya (secondary) (2 people ✅)

Every critical topic has at least 2 people who can defend it. No single point of failure.
