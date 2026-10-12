import asyncio
from playwright.async_api import async_playwright

async def main():
    prompt_text = "Cinematic video clip, slow camera push in, glowing futuristic computer terminal in misty laboratory, moody neon lighting, photorealistic 8k, aspect ratio 9:16 vertical"
    
    print("Connecting to Chrome on port 9222...")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        
        flow_pages = [page for page in context.pages if "flow.google.com" in page.url]
        if not flow_pages:
            print("[HATA] Google Flow sekmesi bulunamadı!")
            return
            
        page = flow_pages[0]
        print("Flow sekmesi bulundu:", page.url)

        # ProseMirror editörüne odaklan
        print("ProseMirror istem kutusuna tıklanıyor...")
        editor = page.locator("div.ProseMirror").first
        await editor.click()
        await page.wait_for_timeout(500)

        print(f"Prompt yazılıyor: '{prompt_text[:50]}...'")
        # İstem kutusuna metni yaz
        await editor.fill(prompt_text)
        await page.wait_for_timeout(1000)

        # 'Oluşturmaya başla' butonuna tıkla
        print("'Oluşturmaya başla' butonuna tıklanıyor...")
        btn = page.locator("button[aria-label='Oluşturmaya başla']").first
        if await btn.is_visible():
            await btn.click()
            print("Butona tıklandı!")
        else:
            print("Buton görünmedi, Enter'a basılıyor...")
            await editor.press("Enter")

        print("5 saniye bekleniyor...")
        await page.wait_for_timeout(5000)

        screenshot_path = "flow_generation_started.png"
        await page.screenshot(path=screenshot_path)
        print(f"Ekran görüntüsü kaydedildi: {screenshot_path}")

if __name__ == "__main__":
    asyncio.run(main())
