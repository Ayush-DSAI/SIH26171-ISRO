from pathlib import Path


async def capture_page(page, output_filename: str) -> str:
    output_dir = Path("tmp")
    output_dir.mkdir(exist_ok=True)

    if not output_filename.lower().endswith(".png"):
        output_filename += ".png"

    output_path = output_dir / output_filename

    await page.set_viewport_size({"width": 1280, "height": 720})
    await page.screenshot(path=str(output_path), full_page=False)

    return str(output_path.resolve())
