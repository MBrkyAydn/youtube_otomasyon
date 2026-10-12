import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        flow_pages = [page for page in context.pages if "flow.google.com" in page.url]
        page = flow_pages[0]

        # 1. Video elements
        videos = await page.locator("video").all()
        print(f"Total videos in editor view: {len(videos)}")
        for i, v in enumerate(videos):
            src = await v.get_attribute("src")
            print(f"Video {i} src: {src}")

        # 2. Buttons
        buttons = await page.locator("button").all()
        print(f"Total buttons: {len(buttons)}")
        for i, b in enumerate(buttons):
            label = await b.get_attribute("aria-label")
            txt = (await b.inner_text()).strip()
            if label or txt:
                print(f"Button {i}: aria-label='{label}', text='{txt}'")

asyncio.run(inspect())
