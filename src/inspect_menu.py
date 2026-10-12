import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        flow_pages = [page for page in context.pages if "flow.google.com" in page.url]
        page = flow_pages[0]

        tiles = await page.locator("flow-video-tile").all()
        print(f"Total tiles: {len(tiles)}")
        for idx, t in enumerate(tiles):
            v_count = len(await t.locator("video").all())
            print(f"Tile {idx}: video count = {v_count}")
            if v_count > 0:
                v = t.locator("video").first
                src = await v.get_attribute("src")
                print(f"Tile {idx} video src: {src[:70]}...")

        # Also check Tile 0 to see if video is ready now
        tile0_videos = await tiles[0].locator("video").all()
        print(f"Tile 0 videos count now: {len(tile0_videos)}")

        # Check menu
        more_btn = tiles[1].locator('button[aria-label*="seçenekler"]').first
        if await more_btn.is_visible():
            await more_btn.click()
            await page.wait_for_timeout(1000)
            items = await page.locator('[role="menuitem"], button.mat-mdc-menu-item').all()
            print(f"Found {len(items)} menu items:")
            for item in items:
                print("  Item:", (await item.inner_text()).strip())

asyncio.run(inspect())
