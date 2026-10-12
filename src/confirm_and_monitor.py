import asyncio
from playwright.async_api import async_playwright

async def main():
    print("Connecting to Chrome on 9222...")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        flow_pages = [page for page in context.pages if "flow.google.com" in page.url]
        if not flow_pages:
            print("[HATA] Google Flow sekmesi bulunamadı!")
            return
            
        page = flow_pages[0]
        print(f"Flow sekmesi bulundu: {page.url} | Başlık: {await page.title()}")

        btn_always = page.locator('button:has-text("Her zaman onayla")').first
        btn_confirm = page.locator('button:has-text("Onayla")').first

        if await btn_always.is_visible():
            print("Bulundu: 'Her zaman onayla', tıklanıyor...")
            await btn_always.click()
            print("Tıklandı!")
        elif await btn_confirm.is_visible():
            print("Bulundu: 'Onayla', tıklanıyor...")
            await btn_confirm.click()
            print("Tıklandı!")
        else:
            print("Onay penceresi şu anda görünmüyor.")

        await page.wait_for_timeout(3000)
        screenshot_path = "flow_current_state.png"
        await page.screenshot(path=screenshot_path)
        print(f"Ekran görüntüsü kaydedildi: {screenshot_path}")

if __name__ == "__main__":
    asyncio.run(main())
