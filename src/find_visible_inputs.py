import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [page for page in context.pages if "flow.google.com" in page.url][0]

        # Görünür tüm input ve düzenlenebilir alanları tara
        locators = await page.locator("input:visible, textarea:visible, [contenteditable='true']:visible, div[role='textbox']:visible").all()
        print(f"Toplam Görünür Alan Sayısı: {len(locators)}")
        for idx, loc in enumerate(locators):
            tag = await loc.evaluate("el => el.tagName")
            cl = await loc.get_attribute("class")
            ph = await loc.get_attribute("placeholder")
            aria = await loc.get_attribute("aria-label")
            text = (await loc.inner_text()).strip()
            print(f"[{idx}] Tag={tag} | Placeholder='{ph}' | Aria='{aria}' | Class='{cl}' | Text='{text}'")

if __name__ == "__main__":
    asyncio.run(main())
