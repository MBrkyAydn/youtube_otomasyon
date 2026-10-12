import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        
        # Ekran görüntüsü al
        screenshot_path = "flow_screenshot.png"
        await page.screenshot(path=screenshot_path)
        print("Screenshot saved to:", screenshot_path)

        # Butonları ve linkleri listele
        elements = await page.locator("button, a").all()
        print("Bulunan Buton ve Linkler:")
        for el in elements[:20]:
            try:
                txt = (await el.inner_text()).strip()
                href = await el.get_attribute("href")
                if txt or href:
                    print(f"  - Metin: '{txt}' | Href: {href}")
            except Exception:
                pass

if __name__ == "__main__":
    asyncio.run(main())
