import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        flow_pages = [page for page in context.pages if "flow.google.com" in page.url]
        page = flow_pages[0]

        btn_araclar = page.locator('text="Araçlar"').first
        if await btn_araclar.is_visible():
            await btn_araclar.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path="flow_araclar.png")
            print("Araçlar clicked, screenshot saved: flow_araclar.png")

asyncio.run(check())
