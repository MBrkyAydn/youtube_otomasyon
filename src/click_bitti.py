import asyncio
from playwright.async_api import async_playwright

async def click_bitti():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        flow_pages = [page for page in context.pages if "flow.google.com" in page.url]
        page = flow_pages[0]

        btn_bitti = page.locator('button:has-text("Bitti")').first
        if await btn_bitti.is_visible():
            print("Bitti butonuna tıklanıyor...")
            await btn_bitti.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="flow_after_bitti.png")
            print("Screenshot saved: flow_after_bitti.png")
        else:
            print("Bitti butonu görünmüyor.")

asyncio.run(click_bitti())
