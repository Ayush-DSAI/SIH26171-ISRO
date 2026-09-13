import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from browser.screenshot import capture_page
from browser.dom_extractor import extract_dom
from agent.executor import execute_action


# ---------------------------------------------------------------------------
# Grounding helpers
# ---------------------------------------------------------------------------

def _default_mock_grounding() -> dict:
    return {
        "element": "Login button",
        "bbox": [342, 280, 120, 40],
        "confidence": 0.91,
        "raw_response": "mocked",
    }


def _load_aditi_grounding():
    try:
        from perception.grounding import ground_element
        return ground_element
    except Exception:
        return None


async def _ground_element(task: str, mock_grounding: bool, image_path: str) -> dict:
    if not mock_grounding:
        ground_fn = _load_aditi_grounding()
        if ground_fn is not None:
            try:
                result = await ground_fn(task, image_path)
                if isinstance(result, dict) and "bbox" in result:
                    return result
            except Exception:
                pass
    return _default_mock_grounding()


# ---------------------------------------------------------------------------
# PII Redaction (mocked — real MediaPipe / NER integration goes here Day 8)
# ---------------------------------------------------------------------------

def mock_redact(image_path: str, dom_json: dict) -> dict:
    """
    Simulates on-device PII redaction.

    In the real pipeline this will:
      - Run MediaPipe FaceDetection on `image_path` → blur detected faces.
      - Run a lightweight NER / regex pass on `dom_json` → mask passwords,
        phone numbers, e-mail addresses, Aadhaar numbers, etc.
      - Write the sanitized image to tmp/ and return its path.

    Returns a structured redaction report consumed by api.py's broadcast.
    """
    detected_pii = [
        {"type": "password", "source": "dom"},
        {"type": "face",     "source": "mediapipe"},
    ]
    return {
        "sanitized_image_path": image_path,   # real impl → new file path
        "detected_pii": detected_pii,
    }


# ---------------------------------------------------------------------------
# Remote VLM Consultation (mocked — real HTTPS call goes here Day 8)
# ---------------------------------------------------------------------------

def mock_ask_remote(sanitized_image_path: str, task: str) -> str:
    """
    Simulates querying a remote Vision-Language Model (VLM) with the
    *already-redacted* screenshot so no raw PII ever leaves the device.

    Real implementation will:
      - Base-64 encode the sanitized image at `sanitized_image_path`.
      - POST to a remote VLM endpoint (Gemini / GPT-4o / internal API).
      - Return the model's natural-language action recommendation.
    """
    # MOCKED - replace with real API call later
    return (
        "Based on the interface, I recommend clicking the Login button "
        "located at the bottom of the form."
    )


# ---------------------------------------------------------------------------
# Core agent step
# ---------------------------------------------------------------------------

async def run_agent_step(
    page,
    task: str,
    mock_grounding: bool = True,
    grounding_override: dict | None = None,
) -> dict:
    # 1. Capture before-state
    before_image = await capture_page(page, "before_action.png")

    # 2. Extract DOM for grounding + redaction context
    dom_json = await extract_dom(page)

    # 3. Grounding — map task → bounding box
    if grounding_override is not None:
        grounding = grounding_override
    else:
        grounding = await _ground_element(task, mock_grounding, before_image)

    # 4. PII Redaction (mocked)
    redaction = mock_redact(before_image, dom_json)

    # 5. Remote VLM consultation on the sanitized image (mocked)
    remote_response = mock_ask_remote(
        sanitized_image_path=redaction["sanitized_image_path"],
        task=task,
    )

    # 6. Execute the action
    bbox = grounding.get("bbox")
    execution = await execute_action(page, action_type="click", bbox=bbox)

    await asyncio.sleep(0.5)

    # 7. Capture after-state
    after_image = await capture_page(page, "after_action.png")

    return {
        "task":                   task,
        "before_image":           before_image,
        "after_image":            after_image,
        "grounding":              grounding,
        "execution":              execution,
        "redaction":              redaction,
        "sanitized_image_path":   redaction["sanitized_image_path"],
        "remote_response":        remote_response,
    }
