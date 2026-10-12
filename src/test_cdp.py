import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        print("Connected to Chrome successfully!")
        context = browser.contexts[0]
        print(f"Total Pages: {len(context.pages)}")
        for idx, page in enumerate(context.pages):
            print(f"  Page {idx + 1}: Title='{await page.title()}' | URL={page.url}")

if __name__ == "__main__":
    asyncio.run(main())
