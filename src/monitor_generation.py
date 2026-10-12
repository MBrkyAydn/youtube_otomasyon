import asyncio
import time
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
        print(f"Flow sekmesi bulundu: {page.url}")

        # Bekleme döngüsü (video üretimi genellikle 30-90 saniye sürer)
        print("Video üretiminin tamamlanması bekleniyor...")
        start_time = time.time()
        
        while time.time() - start_time < 180:
            # Durdur butonunu veya üretim göstergelerini kontrol et
            # Alt kısımdaki yuvarlak kare stop butonu: button with stop icon
            stop_btn = page.locator("button:has(svg.stop-icon), button[aria-label*='Durdur'], button[aria-label*='Stop']").first
            is_generating = await stop_btn.is_visible()
            
            # Ayrıca video etiketlerini kontrol et
            videos = await page.locator("video").all()
            print(f"[{int(time.time() - start_time)}s] Üretim devam ediyor mu? {is_generating} | Bulunan video elementi: {len(videos)}")
            
            if not is_generating and len(videos) > 0:
                print("Üretim tamamlanmış görünüyor!")
                break
                
            await page.wait_for_timeout(5000)

        await page.wait_for_timeout(3000)
        await page.screenshot(path="flow_generation_completed.png")
        print("Ekran görüntüsü alındı: flow_generation_completed.png")

        # Video ve indirme butonlarını analiz et
        videos = await page.locator("video").all()
        for i, v in enumerate(videos):
            src = await v.get_attribute("src")
            print(f"Video {i}: src={src}")

        # İndirme butonlarını ara
        download_btns = await page.locator("button[aria-label*='İndir'], button[aria-label*='Download'], a[download]").all()
        print(f"Bulunan indirme butonu sayısı: {len(download_btns)}")
        for i, b in enumerate(download_btns):
            label = await b.get_attribute("aria-label")
            print(f"İndirme butonu {i}: aria-label={label}")

if __name__ == "__main__":
    asyncio.run(main())
