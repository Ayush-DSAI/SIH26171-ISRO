# SIH 2026 ISRO Prototype - Architecture Constraints
- **Stack:** Python 3.11+, FastAPI, Playwright (async), HTML/CSS/Vanilla JS (no React/Vue).
- **No Databases:** Use in-memory state or JSON files.
- **Privacy Core:** NEVER log raw sensitive data.
- **Signatures:**
  - `ground_element(image_path: str, description: str) -> dict`
  - `redact(image_path: str, dom_json: dict) -> dict`
  - `ask_vlm(image_path: str, prompt: str) -> str`