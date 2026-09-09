import asyncio
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent.loop import run_agent_step


async def main():
    project_root = Path(__file__).resolve().parent
    tmp_dir = project_root / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    html_path = project_root / "test_pages" / "login_form.html"
    file_uri = html_path.resolve().as_uri()
    print(f"[test_day3_4] Login page URI: {file_uri}")

    print("[test_day3_4] Launching NON-HEADLESS Chromium browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        print("[test_day3_4] Browser launched with 1280x720 viewport.")

        print("[test_day3_4] Navigating to login_form.html...")
        await page.goto(file_uri, wait_until="domcontentloaded")
        await page.wait_for_timeout(300)
        print("[test_day3_4] Login page loaded.")

        button_locator = page.locator("button#loginBtn")
        raw_box = await button_locator.bounding_box()
        if raw_box is None:
            print("[test_day3_4] WARNING: Could not compute button bbox, using fallback.")
            real_bbox = [342, 280, 120, 40]
        else:
            real_bbox = [
                int(round(raw_box["x"])),
                int(round(raw_box["y"])),
                int(round(raw_box["width"])),
                int(round(raw_box["height"])),
            ]
        print(f"[test_day3_4] Computed real button bbox: {real_bbox}")

        real_grounding = {
            "element": "Login button",
            "bbox": real_bbox,
            "confidence": 0.99,
            "raw_response": "real_dom_bbox",
        }

        task = "Click the Login button"
        print(f"[test_day3_4] Running agent step for task: '{task}'")

        result = await run_agent_step(
            page,
            task=task,
            mock_grounding=True,
            grounding_override=real_grounding,
        )

        print("[test_day3_4] === Agent Step Result ===")
        print(json.dumps(result, indent=2, default=str))

        before_img = Path(result["before_image"])
        after_img = Path(result["after_image"])
        before_exists = before_img.exists()
        after_exists = after_img.exists()
        print(f"[test_day3_4] before_image exists ({before_exists}): {before_img}")
        print(f"[test_day3_4] after_image exists ({after_exists}): {after_img}")

        if not (before_exists and after_exists):
            print("[test_day3_4] ERROR: One or both images are missing!")
            sys.exit(1)

        button_text_after = await button_locator.inner_text()
        print(f"[test_day3_4] Button text after click: '{button_text_after}'")

        await page.wait_for_timeout(800)
        print("[test_day3_4] Closing browser...")
        await browser.close()

    print("[test_day3_4] All tests passed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
