import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        
        # Find the Flow page
        flow_page = None
        for page in context.pages:
            if "flow.google.com" in page.url:
                flow_page = page
                break
        
        if not flow_page:
            print("Flow page not found!")
            return

        print("Found Flow Page:", flow_page.url)
        await flow_page.screenshot(path="flow_logged_in.png")
        print("Screenshot saved to flow_logged_in.png")

        # Find inputs, textareas, and buttons
        inputs = await flow_page.locator("textarea, input, [contenteditable='true']").all()
        print(f"Total Inputs/Textareas: {len(inputs)}")
        for idx, inp in enumerate(inputs[:10]):
            try:
                placeholder = await inp.get_attribute("placeholder")
                aria_label = await inp.get_attribute("aria-label")
                tag = await inp.evaluate("el => el.tagName")
                print(f"  Input {idx+1}: Tag={tag}, Placeholder='{placeholder}', Aria='{aria_label}'")
            except Exception as e:
                pass

        buttons = await flow_page.locator("button").all()
        print(f"\nTotal Buttons: {len(buttons)}")
        for idx, btn in enumerate(buttons[:15]):
            try:
                txt = (await btn.inner_text()).strip()
                aria = await btn.get_attribute("aria-label")
                if txt or aria:
                    print(f"  Button {idx+1}: Text='{txt}' | Aria='{aria}'")
            except Exception:
                pass

if __name__ == "__main__":
    asyncio.run(main())
