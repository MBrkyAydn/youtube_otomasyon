import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        flow_pages = [page for page in context.pages if "flow.google.com" in page.url]
        page = flow_pages[0]

        # 1. Element at (280, 100)
        info = await page.evaluate('''() => {
            const el = document.elementFromPoint(280, 100);
            if (!el) return null;
            return {
                tagName: el.tagName,
                className: el.className,
                id: el.id,
                outer: el.outerHTML.slice(0, 300),
                parentOuter: el.parentElement ? el.parentElement.outerHTML.slice(0, 300) : null
            };
        }''')
        print("Point (280, 100) info:", info)

        # 2. Check if a new video has appeared now (maybe render just finished)
        videos = await page.locator("video").all()
        print("Total videos now:", len(videos))
        for i, v in enumerate(videos):
            src = await v.get_attribute("src")
            box = await v.bounding_box()
            print(f"Video {i}: box={box}, src={src}")

asyncio.run(inspect())
