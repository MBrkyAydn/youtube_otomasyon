import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        flow_pages = [page for page in context.pages if "flow.google.com" in page.url]
        page = flow_pages[0]

        # Model butonunu ara
        model_btn = page.locator('button:has-text("Omni"), button:has-text("Veo")').first
        if await model_btn.is_visible():
            print("Model butonu bulundu:", (await model_btn.inner_text()).strip())
            await model_btn.click()
            await page.wait_for_timeout(1000)
            items = await page.locator('[role="menuitem"], .mat-mdc-menu-item').all()
            print(f"Toplam {len(items)} model seçeneği:")
            for item in items:
                print("  -", (await item.inner_text()).strip())
            await page.screenshot(path="flow_models.png")
        else:
            print("Model butonu doğrudan görünmedi.")

asyncio.run(inspect())
