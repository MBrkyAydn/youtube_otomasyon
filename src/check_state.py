import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        flow_pages = [page for page in context.pages if "flow.google.com" in page.url]
        page = flow_pages[0]

        btn_bitti = page.locator('button:has-text("Bitti")').first
        if await btn_bitti.is_visible():
            print("Currently in editor view, clicking Bitti to return to canvas...")
            await btn_bitti.click()
            await page.wait_for_timeout(2000)

        tiles = await page.locator("flow-video-tile").count()
        print(f"Total tiles on canvas: {tiles}")

asyncio.run(check())
