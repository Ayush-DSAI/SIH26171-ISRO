import asyncio
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))

from browser.screenshot import capture_page
from browser.dom_extractor import extract_dom


async def main():
    project_root = Path(__file__).resolve().parent
    tmp_dir = project_root / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    html_path = project_root / "test_pages" / "login_form.html"
    file_uri = html_path.resolve().as_uri()
    print(f"[test_day2] Login page URI: {file_uri}")

    print("[test_day2] Launching headless Chromium browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        print("[test_day2] Browser launched with 1280x720 viewport.")

        print("[test_day2] Navigating to login_form.html...")
        await page.goto(file_uri, wait_until="domcontentloaded")
        print("[test_day2] Login page loaded successfully.")

        print("[test_day2] Capturing screenshot (login_test.png)...")
        screenshot_path = await capture_page(page, "login_test.png")
        print(f"[test_day2] Screenshot saved to: {screenshot_path}")

        print("[test_day2] Extracting DOM accessibility tree...")
        dom_tree = await extract_dom(page)
        dom_output = tmp_dir / "dom_test.json"
        with open(dom_output, "w", encoding="utf-8") as f:
            json.dump(dom_tree, f, indent=2, default=str)
        print(f"[test_day2] DOM tree dumped to: {dom_output.resolve()}")
        print(f"[test_day2] DOM tree contains {len(json.dumps(dom_tree))} chars of JSON.")

        print("[test_day2] Closing browser...")
        await browser.close()

    print("[test_day2] All tasks completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
