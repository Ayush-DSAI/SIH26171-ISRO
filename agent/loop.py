import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from browser.screenshot import capture_page
from agent.executor import execute_action


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


async def run_agent_step(
    page,
    task: str,
    mock_grounding: bool = True,
    grounding_override: dict | None = None,
) -> dict:
    before_image = await capture_page(page, "before_action.png")

    if grounding_override is not None:
        grounding = grounding_override
    else:
        grounding = await _ground_element(task, mock_grounding, before_image)

    bbox = grounding.get("bbox")
    execution = await execute_action(page, action_type="click", bbox=bbox)

    await asyncio.sleep(0.5)

    after_image = await capture_page(page, "after_action.png")

    return {
        "task": task,
        "before_image": before_image,
        "after_image": after_image,
        "grounding": grounding,
        "execution": execution,
    }
