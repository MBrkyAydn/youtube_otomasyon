import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [p for p in context.pages if "flow.google.com" in p.url][0]

        # Input alanını bul
        prompt_input = page.locator("[placeholder*='oluşturmak'], [aria-label*='oluşturmak'], textarea, input, [contenteditable='true']").first
        print("Prompt Input tag:", await prompt_input.evaluate("el => el.tagName"))
        print("Prompt Input placeholder:", await prompt_input.get_attribute("placeholder"))

        # Submit / Gönder butonunu bul
        send_buttons = await page.locator("button").all()
        for idx, btn in enumerate(send_buttons):
            aria = await btn.get_attribute("aria-label")
            txt = (await btn.inner_text()).strip()
            if aria or "arrow" in (await btn.inner_html()):
                print(f"Button {idx}: text='{txt}', aria='{aria}'")

if __name__ == "__main__":
    asyncio.run(main())
