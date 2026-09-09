# PART 8 — WINNING DEMO (3–5 Minutes)

---

## DEMO PHILOSOPHY

> "Don't tell the jury about privacy. SHOW them privacy being violated in Baseline A, and then SHOW them our system preventing it."

The demo must be **visually undeniable**. When the jury sees the before/after screenshots, they should immediately understand the privacy value.

---

## DEMO SCRIPT (4 minutes)

### [0:00 – 0:30] CONTEXT SETUP

**Narrator (Nidhi or Himanshu):**

> "Browser agents automate web interactions — filling forms, booking tickets, navigating dashboards. But every screenshot they take contains sensitive information: passwords, Aadhaar numbers, email addresses, even faces. Current browser agents send these RAW screenshots to cloud AI models. We solve this."

**Screen:** Show a simple animation/slide of a traditional agent workflow (screenshot → cloud → action) with a red "PRIVACY RISK" label.

---

### [0:30 – 1:00] THE PROBLEM — BASELINE DEMO

**Action:** Open the test webpage (registration form with):
- Username field filled: "Rajesh Kumar"
- Password field filled: "••••••••" (value: MyS3cretP@ss)
- Email filled: "rajesh@example.com"
- Phone: "+91 98765 43210"
- Aadhaar: "2345 6789 0123"
- A profile photo with a face

**Screen:** Take a full screenshot. Show it. Say:

> "This is what a traditional browser agent would send to a cloud model. The password, Aadhaar number, phone, email, and face are ALL visible. This is a privacy disaster."

**Show:** The raw screenshot with all PII highlighted in red boxes.

---

### [1:00 – 2:00] OUR SOLUTION — LIVE REDACTION DEMO

**Action:** Run our agent on the same page.

**Screen (3-panel view):**

| Left Panel | Center Panel | Right Panel |
|------------|--------------|-------------|
| Original Screenshot | Detected PII (highlighted) | Sanitized Screenshot |

**Step-by-step:**

1. **DOM Scan (5ms):** Password field detected via `type="password"` → highlighted in blue
2. **DOM Scan (5ms):** Email field detected via `type="email"` → highlighted in blue
3. **Regex Layer (15ms):** Aadhaar number "2345 6789 0123" detected → highlighted in yellow
4. **Regex Layer (8ms):** Phone "+91 98765 43210" detected → highlighted in yellow
5. **Face Detection (20ms):** Profile photo face detected → highlighted in green
6. **Redaction Applied:**
   - Password: ████████████
   - Email: ████████████████
   - Aadhaar: ████████████
   - Phone: ██████████████
   - Face: [BLURRED]

**Narration:**
> "In under 50 milliseconds, our system detected 5 sensitive elements using 3 different techniques — DOM analysis, regex pattern matching, and face detection. Now watch the sanitized version."

**Show:** Sanitized screenshot — same page layout visible, all PII masked. The UI is still understandable for reasoning. The data is gone.

---

### [2:00 – 2:45] HYBRID REASONING — LOCAL + REMOTE

**Action:** Give the agent a task: "Fill in the search bar and submit"

**Screen:** Show the agent loop in real-time:

```
Step 1: [LOCAL] Screenshot captured (45ms)
Step 2: [LOCAL] VLM perception: "Registration form with fields..." (320ms)
Step 3: [LOCAL] PII detected: 5 regions (48ms)
Step 4: [LOCAL] Screenshot sanitized (35ms)
Step 5: [ROUTING] Task requires planning → REMOTE
Step 6: [REMOTE] Sanitized screenshot sent to cloud model
Step 7: [REMOTE] Response: "Click search bar at (450, 200)" (1.2s)
Step 8: [LOCAL] Action executed: click(450, 200) (80ms)
Step 9: [LOCAL] Verification: Page changed ✅ (50ms)
```

**Narration:**
> "The local model handles perception in 320 milliseconds. When complex reasoning is needed, ONLY the sanitized screenshot goes to the cloud. The cloud model never sees the password, never sees the face, never sees the Aadhaar number."

**Key visual:** Show the sanitized screenshot next to the words "THIS is what the cloud model sees."

---

### [2:45 – 3:30] METRICS DASHBOARD

**Screen:** Show the demo UI metrics panel:

```
┌────────────────────────────────────────┐
│           PERFORMANCE METRICS          │
├────────────────────────────────────────┤
│ Local VLM Inference:    320ms          │
│ PII Detection:          48ms           │
│ Redaction:              35ms           │
│ Remote Reasoning:       1,200ms        │
│ Action Execution:       80ms           │
│ Verification:           50ms           │
│ ─────────────────────────────────      │
│ Total End-to-End:       1,733ms        │
│                                        │
│ VRAM Usage:             3.8 GB / 8 GB  │
│ RAM Usage:              2.1 GB         │
│ CPU Usage:              15%            │
│                                        │
│ PII Detection:                         │
│   Precision:  96.5%                    │
│   Recall:     99.1%                    │
│   F1 Score:   97.8%                    │
│                                        │
│ Privacy Status: ██████████ SECURE      │
│ Raw PII sent to cloud: 0 items ✅      │
└────────────────────────────────────────┘
```

**Narration:**
> "Every metric is measured, not claimed. 99.1% recall means out of 100 sensitive fields, we catch 99. The remaining 1% triggers our fallback — we BLOCK the outbound request entirely if we can't guarantee safety."

---

### [3:30 – 4:00] ARCHITECTURE SUMMARY + CLOSE

**Screen:** Clean architecture diagram

**Narration:**
> "Our architecture is a three-layer defense: DOM analysis for tagged fields, regex for patterned data, and computer vision for faces and rendered text. Everything sensitive stays on-device. The cloud only reasons over what's safe to share. This is privacy by architecture, not by policy."

**Final slide:** Project name, team, ISRO logo, key metrics.

---

## DEMO PREPARATION CHECKLIST

- [ ] Test page loaded and verified (all PII visible)
- [ ] llama-server running (GPU warm, first inference already done)
- [ ] Remote model API key configured and tested
- [ ] Demo UI open in split-screen
- [ ] Backup plan: pre-recorded video if live demo fails
- [ ] Internet connectivity verified (for remote model)
- [ ] Fallback: local-only mode demo if internet fails
- [ ] Narration script printed/memorized
- [ ] Timer visible to speaker

## DEMO FAILURE FALLBACKS

| Failure | Fallback |
|---------|----------|
| llama-server crashes | Switch to pre-recorded video segment |
| Internet down | Demo local-only mode (still shows redaction) |
| Redaction misses PII | Have a scripted explanation: "Our post-redaction verifier would catch this and block the outbound request" |
| Action clicks wrong element | Show it as a feature: "The agent detects the failure, re-evaluates, and self-corrects" |
| VRAM OOM | Pre-warm the model 5 minutes before demo. Have Ollama as backup. |
