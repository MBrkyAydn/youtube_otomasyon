import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        flow_page = [p for p in context.pages if "flow.google.com" in p.url][0]
        
        print("Clicking '+ Yeni proje'...")
        # Yeni proje butonuna tıkla
        btn = flow_page.locator("text=Yeni proje").first
        await btn.click()
        
        await flow_page.wait_for_timeout(4000)
        print("Studio URL:", flow_page.url)
        await flow_page.screenshot(path="flow_studio_inside.png")
        print("Saved flow_studio_inside.png")

if __name__ == "__main__":
    asyncio.run(main())
