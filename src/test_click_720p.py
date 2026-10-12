import asyncio
import os
from playwright.async_api import async_playwright

async def download_720p():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        flow_pages = [page for page in context.pages if "flow.google.com" in page.url]
        page = flow_pages[0]

        # Menü şu an açık olabilir veya tekrar açalım
        menu_opt = page.locator('text="720p"').first
        if not await menu_opt.is_visible():
            print("Download butonuna tıklanıyor...")
            btn_download = page.locator("button[aria-label*='indir' i]").first
            await btn_download.click()
            await page.wait_for_timeout(1000)

        print("720p seçeneği tıklanıyor ve indirme bekleniyor...")
        async with page.expect_download(timeout=30000) as download_info:
            await page.locator('text="720p"').first.click()

        download = await download_info.value
        filename = download.suggested_filename
        print(f"İndirme yakalandı! Dosya: {filename}")

        os.makedirs("projects/tek_sahne_test/klipler", exist_ok=True)
        target = "projects/tek_sahne_test/klipler/scene_1.mp4"
        await download.save_as(target)
        print(f"Kaydedildi: {target} ({os.path.getsize(target)/(1024*1024):.2f} MB)")

asyncio.run(download_720p())
