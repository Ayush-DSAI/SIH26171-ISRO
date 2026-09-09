import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    # Ensure local tmp directory exists
    output_dir = Path("tmp")
    output_dir.mkdir(exist_ok=True)
    screenshot_path = output_dir / "google_test.png"

    async with async_playwright() as p:
        # headless=False lets you visually observe the browser in real time
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        print("Navigating to Google...")
        await page.goto("https://www.google.com", wait_until="networkidle")

        print(f"Capturing screenshot to {screenshot_path}...")
        await page.screenshot(path=str(screenshot_path))

        print("Done! Closing browser.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())