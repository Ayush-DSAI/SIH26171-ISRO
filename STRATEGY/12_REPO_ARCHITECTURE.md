# PART 12 — REPOSITORY / SOFTWARE ARCHITECTURE

---

## DIRECTORY STRUCTURE

```
/browser-agent/
│
├── README.md                    # Project overview, setup, architecture diagram
├── LICENSE                      # Apache 2.0
├── pyproject.toml               # Python project config (dependencies, scripts)
├── requirements.txt             # Pinned dependencies
├── .env.example                 # Template for API keys and paths
├── .gitignore                   # Model files, venv, __pycache__, screenshots
│
├── configs/
│   ├── agent.yaml               # Agent loop config (max iterations, timeouts)
│   ├── models.yaml              # Model paths, context size, GPU layers
│   ├── privacy.yaml             # PII patterns, redaction strategies, thresholds
│   └── demo.yaml                # Demo-specific settings
│
├── src/
│   ├── __init__.py
│   │
│   ├── agent/                   # AYUSH — Agent orchestration
│   │   ├── __init__.py
│   │   ├── loop.py              # Main agent loop (observe→think→act→verify)
│   │   ├── planner.py           # Task decomposition, action selection
│   │   ├── executor.py          # Action execution (Playwright commands)
│   │   ├── router.py            # Local vs remote routing decision
│   │   └── state.py             # Conversation state, task progress tracking
│   │
│   ├── perception/              # ADITI — Visual understanding
│   │   ├── __init__.py
│   │   ├── vlm_client.py        # Client for llama-server (OpenAI-compat API)
│   │   ├── grounding.py         # Element localization (screenshot + desc → bbox)
│   │   ├── prompts.py           # Prompt templates for perception/grounding/action
│   │   ├── ocr.py               # OCR integration (VLM-based or PaddleOCR)
│   │   └── preprocessing.py     # Image resize, format conversion, normalization
│   │
│   ├── privacy/                 # ABHISHEK — PII detection + redaction
│   │   ├── __init__.py
│   │   ├── detector.py          # Multi-layer PII detection orchestrator
│   │   ├── dom_scanner.py       # DOM attribute-based PII detection
│   │   ├── regex_engine.py      # Regex patterns for Aadhaar, PAN, email, phone
│   │   ├── face_detector.py     # MediaPipe face detection wrapper
│   │   ├── redactor.py          # Apply masks/blur to screenshots
│   │   ├── verifier.py          # Post-redaction re-scan verification
│   │   └── patterns.py          # PII pattern definitions + validation (Verhoeff, Luhn)
│   │
│   ├── browser/                 # AYUSH (+ NIDHI for testing)
│   │   ├── __init__.py
│   │   ├── controller.py        # Playwright browser management
│   │   ├── screenshot.py        # Screenshot capture with configurable resolution
│   │   ├── dom_extractor.py     # Accessibility tree + DOM attribute extraction
│   │   └── actions.py           # Click, type, scroll, navigate wrappers
│   │
│   ├── server/                  # HIMANSHU
│   │   ├── __init__.py
│   │   ├── api.py               # FastAPI app (REST endpoints)
│   │   ├── websocket.py         # WebSocket handler for real-time updates
│   │   ├── middleware.py        # Privacy gateway middleware
│   │   ├── schemas.py           # Pydantic request/response models
│   │   └── telemetry.py         # Timing/metrics collection + /metrics endpoint
│   │
│   ├── models/                  # SHAURYA
│   │   ├── __init__.py
│   │   ├── local_inference.py   # Wrapper for llama-server calls
│   │   ├── remote_inference.py  # Cloud model API client
│   │   ├── verification.py      # Screenshot diff + action verification
│   │   └── vram_monitor.py      # GPU memory monitoring utility
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py            # YAML config loader
│       ├── logging.py           # PII-safe structured JSON logger
│       └── image_utils.py       # Common image manipulation functions
│
├── frontend/                    # AYUSH — Demo UI
│   ├── index.html               # Single-page demo dashboard
│   ├── style.css                # Dashboard styles
│   └── app.js                   # WebSocket client + UI logic
│
├── tests/                       # ABHISHEK (core) + ALL (per module)
│   ├── __init__.py
│   ├── test_pii_detection.py    # Unit tests for all PII patterns
│   ├── test_redaction.py        # Redaction quality tests
│   ├── test_grounding.py        # Grounding accuracy tests
│   ├── test_agent_loop.py       # Integration tests for agent loop
│   ├── test_privacy_gateway.py  # Privacy middleware tests
│   └── fixtures/                # Test images, DOM snapshots, expected results
│       ├── screenshots/
│       └── dom_samples/
│
├── test_pages/                  # NIDHI — Test HTML pages
│   ├── login_form.html
│   ├── registration_form.html
│   ├── profile_page.html
│   ├── payment_form.html
│   ├── government_form.html
│   ├── social_media.html
│   ├── no_pii.html
│   ├── dynamic_form.html
│   ├── dark_mode.html
│   └── image_pii.html
│
├── benchmarks/                  # ABHISHEK
│   ├── run_benchmarks.py        # Benchmark runner script
│   ├── results/                 # CSV/JSON benchmark outputs
│   └── analysis.py              # Generate charts/tables from results
│
├── docs/                        # HIMANSHU + NIDHI
│   ├── architecture.md          # Detailed architecture document
│   ├── api_spec.md              # API endpoint documentation
│   ├── privacy_model.md         # Security/privacy threat model
│   ├── setup_guide.md           # How to set up + run the system
│   ├── demo_script.md           # Demo narration script
│   └── diagrams/                # Architecture diagrams (PNG/SVG exports)
│
├── scripts/                     # SHAURYA
│   ├── download_model.py        # Download GGUF model from HuggingFace
│   ├── start_llama_server.sh    # Start llama-server with correct flags
│   ├── start_llama_server.bat   # Windows version
│   ├── benchmark_model.py       # Model benchmarking script
│   └── setup_env.sh             # Environment setup script
│
└── .github/
    └── workflows/
        └── lint.yml             # Ruff linting on PRs
```

---

## MODULE OWNERSHIP MAP

| Directory | Primary Owner | Secondary | Review By |
|-----------|--------------|-----------|-----------|
| `src/agent/` | Ayush | Shaurya | Aditi |
| `src/perception/` | Aditi | Ayush | Shaurya |
| `src/privacy/` | Abhishek | Himanshu | Ayush |
| `src/browser/` | Ayush | Nidhi | Abhishek |
| `src/server/` | Himanshu | Ayush | Shaurya |
| `src/models/` | Shaurya | Aditi | Ayush |
| `frontend/` | Ayush | Nidhi | Himanshu |
| `tests/` | Abhishek | Everyone | Ayush |
| `test_pages/` | Nidhi | Abhishek | Ayush |
| `benchmarks/` | Abhishek | Shaurya | Aditi |
| `docs/` | Himanshu | Nidhi | Everyone |
| `scripts/` | Shaurya | Himanshu | Ayush |
| `configs/` | Himanshu | Everyone | Ayush |

---

## GIT WORKFLOW

### Branch Strategy
```
main (protected — stable, deployable)
  └── dev (integration branch — PRs merged here first)
       ├── feat/ayush-agent-loop
       ├── feat/shaurya-model-server
       ├── feat/himanshu-api-gateway
       ├── feat/aditi-grounding
       ├── feat/abhishek-redaction
       └── feat/nidhi-test-pages
```

### PR Rules
- All PRs target `dev` (never directly to `main`)
- 1 reviewer required (owner of the module being touched reviews, or Ayush for integration)
- PR title: `feat: add PII regex engine for Aadhaar/PAN detection`
- Squash merge to keep history clean
- `dev` → `main` merge only when MVP milestone is reached (Ayush approves)

### Commit Convention
```
feat: add new feature
fix: bug fix
docs: documentation change
test: add/modify tests
refactor: code restructure without behavior change
bench: benchmarking related
config: configuration change
```

---

## ENVIRONMENT MANAGEMENT

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys and model paths
```

**.env.example:**
```
# Local model
LLAMA_SERVER_URL=http://127.0.0.1:8081
MODEL_PATH=./models/Qwen3.5-4B-Instruct-Q4_K_M.gguf
MMPROJ_PATH=./models/Qwen3.5-4B-mmproj-f16.gguf

# Remote model (only needed for hybrid mode)
REMOTE_MODEL_API_KEY=your-api-key-here
REMOTE_MODEL_URL=https://api.openai.com/v1/chat/completions
REMOTE_MODEL_NAME=gpt-4o

# Agent config
MAX_ITERATIONS=20
TASK_TIMEOUT_SECONDS=120
SCREENSHOT_RESOLUTION=1280x720
```

---

## SECRETS MANAGEMENT

| Secret | Where | How |
|--------|-------|-----|
| Remote API key | `.env` (local only) | NEVER committed. In `.gitignore`. |
| Model files (*.gguf) | `models/` directory | NEVER committed. Download via script. In `.gitignore`. |
| Test PII data | `test_pages/` | Fake data ONLY. NO real Aadhaar/PAN numbers. |

---

## TESTING STRATEGY

| Level | What | Tool | Who Runs |
|-------|------|------|----------|
| Unit tests | Individual functions (regex, face detection, routing) | pytest | Everyone (their own module) |
| Integration tests | Module combinations (perception → redaction → action) | pytest | Ayush |
| E2E tests | Full agent loop on test pages | Custom script | Abhishek + Nidhi |
| Benchmark tests | Performance measurement | Custom benchmark runner | Abhishek |
| Privacy tests | Verify no PII in outbound data | Privacy gateway + logged requests | Himanshu |

**Test naming:** `test_<module>_<scenario>.py` → `test_pii_detection_aadhaar_with_verhoeff.py`

**Run tests:**
```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_pii_detection.py -v

# Benchmarks (separate, slower)
python benchmarks/run_benchmarks.py
```
