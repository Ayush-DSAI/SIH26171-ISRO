async def execute_action(
    page,
    action_type: str,
    bbox: list[int] | None = None,
    coords: tuple[int, int] | None = None,
    text: str | None = None,
) -> dict:
    click_x: int
    click_y: int

    if bbox is not None:
        x, y, width, height = bbox
        click_x = x + width // 2
        click_y = y + height // 2
    elif coords is not None:
        click_x, click_y = coords
    else:
        raise ValueError("Either bbox or coords must be provided")

    if action_type == "click":
        await page.mouse.click(click_x, click_y)
    elif action_type == "type":
        if text is None:
            raise ValueError("text must be provided for action_type='type'")
        await page.mouse.click(click_x, click_y)
        await page.keyboard.type(text)
    else:
        raise ValueError(f"Unsupported action_type: {action_type}")

    return {
        "status": "success",
        "action": action_type,
        "target": [click_x, click_y],
    }
