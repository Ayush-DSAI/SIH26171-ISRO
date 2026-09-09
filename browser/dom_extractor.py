async def extract_dom(page) -> dict:
    context = page.context
    cdp_session = await context.new_cdp_session(page)
    try:
        ax_tree = await cdp_session.send("Accessibility.getFullAXTree")
    finally:
        await cdp_session.detach()
    return ax_tree if ax_tree is not None else {}
