import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [page for page in context.pages if "flow.google.com" in page.url][0]

        print("Üretimin bitmesi bekleniyor...")
        # 'Durdur' butonu kaybolana kadar bekle (maksimum 120 saniye)
        for i in range(24):
            stop_btn = page.locator("button[aria-label*='Durdur'], button:has-text('Durdur')").first
            is_generating = await stop_btn.is_visible()
            if not is_generating:
                print(f"Üretim tamamlandı! ({i * 5}. saniye)")
                break
            print(f"  Hala üretiliyor... ({i * 5}s)")
            await page.wait_for_timeout(5000)

        # Son ekran görüntüsünü al
        await page.screenshot(path="flow_generation_finished.png")
        print("flow_generation_finished.png kaydedildi.")

        # Üretilen medyaları / videoları listele
        videos = await page.locator("video").all()
        print(f"Sayfadaki video sayısı: {len(videos)}")
        for idx, v in enumerate(videos):
            src = await v.get_attribute("src")
            print(f"  Video {idx+1}: src={src}")

if __name__ == "__main__":
    asyncio.run(main())
