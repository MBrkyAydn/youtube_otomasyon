import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        
        print("Clicking 'Google Flow ile oluştur' button...")
        # Butona tıkla
        btn = page.locator("text=Google Flow ile oluştur").first
        await btn.click()
        
        # 5 saniye bekle
        await page.wait_for_timeout(5000)
        
        print("New URL:", page.url)
        print("New Title:", await page.title())
        await page.screenshot(path="flow_after_click.png")
        print("Saved flow_after_click.png")

if __name__ == "__main__":
    asyncio.run(main())
