import asyncio
from playwright.async_api import async_playwright

async def test_download():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        flow_pages = [page for page in context.pages if "flow.google.com" in page.url]
        page = flow_pages[0]

        btn_download = page.locator("button[aria-label*='indir' i]").first
        print(f"Download button found: {await btn_download.is_visible()}")

        # Intercept download
        print("Tıklanıyor ve indirme bekleniyor...")
        async with page.expect_download(timeout=30000) as download_info:
            await btn_download.click()

        download = await download_info.value
        suggested_filename = download.suggested_filename
        print(f"İndirme yakalandı! Dosya adı: {suggested_filename}")

        target_path = "projects/tek_sahne_test/klipler/scene_1.mp4"
        await download.save_as(target_path)
        print(f"Dosya başarıyla kaydedildi: {target_path}")

        import os
        size_mb = os.path.getsize(target_path) / (1024 * 1024)
        print(f"Dosya boyutu: {size_mb:.2f} MB")

asyncio.run(test_download())
