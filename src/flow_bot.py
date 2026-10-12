"""
Google Flow (Veo) Tam Otomatik Botu.
Chrome CDP (9222) üzerinden Google Flow arayüzüne bağlanır,
sahnelerin promptlarını sırayla girer, üretim bitince sahne düzenleyicisini açıp
720p orijinal videoyu doğrudan proje klasörüne (scene_X.mp4) indirir.
"""

import os
import sys
import json
import time
import asyncio
from typing import Optional, List
from playwright.async_api import async_playwright, Page, BrowserContext

# UTF-8 stdout desteği
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


class FlowBot:
    def __init__(self, cdp_url: Optional[str] = None):
        self.cdp_url = cdp_url or os.getenv("CHROME_CDP_URL", "http://127.0.0.1:9222")

    async def get_flow_page(self, context: BrowserContext) -> Optional[Page]:
        """Açık olan sekmeler arasında Google Flow sayfasını bulur."""
        for p in context.pages:
            if "flow.google.com" in p.url:
                return p
        return None

    async def handle_popups(self, page: Page):
        """Yalnızca aktif modal/dialog pencerelerindeki onay butonlarına tıklar."""
        try:
            dialog = page.locator('div[role="dialog"], mat-dialog-container, .mat-mdc-dialog-container')
            if await dialog.is_visible():
                btn_always = dialog.locator('text="Her zaman onayla"').first
                if await btn_always.is_visible():
                    print("  [FlowBot] Dialog: 'Her zaman onayla' tıklanıyor...")
                    await btn_always.click()
                    await page.wait_for_timeout(1000)
                    return

                btn_confirm = dialog.locator('text="Onayla"').first
                if await btn_confirm.is_visible():
                    print("  [FlowBot] Dialog: 'Onayla' tıklanıyor...")
                    await btn_confirm.click()
                    await page.wait_for_timeout(1000)
        except Exception:
            pass

    async def ensure_canvas_view(self, page: Page):
        """Eğer sahne düzenleme ekranında kalınmışsa 'Bitti'ye tıklayarak tuvale döner."""
        try:
            btn_bitti = page.locator('button:has-text("Bitti"), button[aria-label*="tamamlandı"]').first
            if await btn_bitti.is_visible():
                print("  [FlowBot] Sahne düzenleyicisinden tuvale dönülüyor ('Bitti')...")
                await btn_bitti.click()
                await page.wait_for_timeout(1500)
        except Exception:
            pass

    async def generate_single_scene(
        self,
        page: Page,
        prompt: str,
        output_path: str,
        scene_idx: int,
        timeout_seconds: int = 360
    ) -> bool:
        """Tek bir sahne için prompt girer, üretilmesini bekler, düzenleyiciyi açıp indirir."""
        print(f"\n" + "=" * 60)
        print(f"🎬 [SAHNE {scene_idx}] Üretim Başlatılıyor...")
        print(f"Prompt: {prompt[:90]}...")
        print("=" * 60)

        await self.ensure_canvas_view(page)

        # Mevcut karo sayısını kaydet
        initial_tiles = await page.locator("flow-video-tile").count()
        print(f"  Mevcut karo sayısı: {initial_tiles}")

        # İstem kutusuna odaklan
        editor = page.locator("div.ProseMirror").first
        if not await editor.is_visible():
            import re
            clean_url = re.sub(r"/(tools|history|settings).*$", "", page.url)
            if clean_url != page.url:
                await page.goto(clean_url)
                await page.wait_for_timeout(3000)
                editor = page.locator("div.ProseMirror").first

        if not await editor.is_visible():
            print("  [HATA] İstem kutusu (ProseMirror) bulunamadı!")
            return False

        await editor.click()
        await page.wait_for_timeout(300)
        await editor.fill(prompt)
        await page.wait_for_timeout(500)

        # Üretimi başlat
        btn_start = page.locator("button[aria-label='Oluşturmaya başla']").first
        if await btn_start.is_visible():
            await btn_start.click()
            print("  [FlowBot] 'Oluşturmaya başla' butonuna tıklandı.")
        else:
            print("  [FlowBot] Enter tuşuna basılıyor...")
            await editor.press("Enter")

        # Kısa bekleme ve olası popup kontrolü
        await page.wait_for_timeout(2000)
        await self.handle_popups(page)

        # Yeni karonun gelmesini ve render edilmesini bekle
        print(f"  [FlowBot] Video renderı bekleniyor (Maksimum {timeout_seconds}s)...")
        start_time = time.time()
        new_tile = None

        while time.time() - start_time < timeout_seconds:
            await self.handle_popups(page)
            current_tile_count = await page.locator("flow-video-tile").count()

            # Yeni karo belirdi mi?
            if current_tile_count > initial_tiles:
                # Flow'da en yeni üretilen karo genellikle listenin ilkidir (index 0)
                candidate_tile = page.locator("flow-video-tile").first
                
                # Karonun thumbnail veya video içerip içermediğini kontrol et
                has_thumb = await candidate_tile.locator("img.thumbnail, video").count() > 0
                if has_thumb:
                    # Kuyruk mesajını kontrol et
                    # Eğer chatte 'is waiting in the queue' varsa ve henüz hazır değilse biraz daha bekle
                    new_tile = candidate_tile
                    print(f"  [FlowBot] Yeni sahne karosu tespit edildi! ({int(time.time() - start_time)}s)")
                    break

            await page.wait_for_timeout(5000)

        if not new_tile:
            print(f"  [HATA] Sahne üretimi zaman aşımına uğradı ({timeout_seconds}s)!")
            return False

        # Şimdi karoya tıklayarak sahne düzenleyicisini (studio) aç
        print("  [FlowBot] Sahne düzenleyicisi açılıyor (karoya tıklanıyor)...")
        await page.wait_for_timeout(2000)
        await new_tile.click()
        await page.wait_for_timeout(2500)

        # Medyayı indir butonunun görünmesini bekle
        btn_download = page.locator("button[aria-label*='indir' i]").first
        for _ in range(10):
            if await btn_download.is_visible():
                break
            await page.wait_for_timeout(1000)

        if not await btn_download.is_visible():
            print("  [UYARI] İndirme butonu doğrudan görünmedi, karoya tekrar tıklanıyor...")
            await new_tile.click()
            await page.wait_for_timeout(2000)

        # İndirme butonuna tıkla -> Çözünürlük menüsü açılır
        print("  [FlowBot] İndirme menüsü açılıyor...")
        await btn_download.click()
        await page.wait_for_timeout(1000)

        # 720p seçeneğini bekle ve tıkla (Playwright indirmeyi yakalar)
        opt_720p = page.locator('text="720p"').first
        if not await opt_720p.is_visible():
            print("  [UYARI] 720p seçeneği görünmedi, tekrar indirme butonuna basılıyor...")
            await btn_download.click()
            await page.wait_for_timeout(1000)

        print("  [FlowBot] 720p (Orijinal Boyut) indiriliyor...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        async with page.expect_download(timeout=45000) as download_info:
            await opt_720p.click()

        download = await download_info.value
        await download.save_as(output_path)

        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  [OK] Sahne {scene_idx} başarıyla indirildi: {output_path} ({file_size_mb:.2f} MB)")

        # 'Bitti' butonuna basarak tuvale geri dön
        await self.ensure_canvas_view(page)
        return True

    async def run_project(self, project_name: str) -> bool:
        """Bir projedeki tüm eksik sahneleri Google Flow ile otomatik üretir."""
        project_dir = os.path.join("projects", project_name)
        json_path = os.path.join(project_dir, "project.json")

        if not os.path.exists(json_path):
            print(f"[HATA] Proje bulunamadı: {json_path}")
            return False

        with open(json_path, "r", encoding="utf-8") as f:
            project_data = json.load(f)

        scenes = project_data.get("scenes", [])
        klipler_dir = os.path.join(project_dir, "klipler")
        os.makedirs(klipler_dir, exist_ok=True)

        print("\n" + "=" * 65)
        print(f"  GOOGLE FLOW OTOMASYON BAŞLADI: {project_name.upper()}")
        print(f"  Toplam Sahne: {len(scenes)}")
        print("=" * 65)

        async with async_playwright() as p:
            try:
                browser = await p.chromium.connect_over_cdp(self.cdp_url)
            except Exception as e:
                print(f"[HATA] Chrome CDP (9222) bağlantı hatası: {e}")
                return False

            context = browser.contexts[0]
            page = await self.get_flow_page(context)
            if not page:
                print("[HATA] Açık Flow sekmesi bulunamadı!")
                return False

            print(f"[FlowBot] Bağlanıldı: {page.url}\n")

            import re
            clean_url = re.sub(r"/(tools|history|settings).*$", "", page.url)
            if clean_url != page.url:
                print(f"[FlowBot] Alt menüden ana tuvale dönülüyor: {clean_url}")
                await page.goto(clean_url)
                await page.wait_for_timeout(3000)

            for idx, scene in enumerate(scenes, 1):
                clip_filename = f"scene_{idx}.mp4"
                clip_path = os.path.join(klipler_dir, clip_filename)

                # Daha önce indirilmişse atla
                if os.path.exists(clip_path) and os.path.getsize(clip_path) > 100 * 1024:
                    print(f"[Sahne {idx}/{len(scenes)}] ZATEN MEVCUT -> {clip_filename}, atlanıyor.")
                    continue

                prompt = scene.get("flow_prompt", "")
                if not prompt:
                    visual = scene.get("visual", "")
                    motion = scene.get("motion", "cinematic camera movement")
                    mode = project_data.get("mode", "shorts")
                    aspect = "9:16 vertical" if mode == "shorts" else "16:9 horizontal"
                    prompt = f"Cinematic video clip, {motion}, {visual}, photorealistic 8k, aspect ratio {aspect}"

                success = await self.generate_single_scene(page, prompt, clip_path, idx)
                if not success:
                    print(f"[HATA] Sahne {idx} üretilemedi! Otomasyon durduruldu.")
                    return False

                # Sahneler arası kısa nefes payı
                await page.wait_for_timeout(3000)

            print("\n" + "=" * 65)
            print(f"[TEBRİKLER] '{project_name}' projesinin tüm video klipleri hazır!")
            print(f"Klipler: {os.path.abspath(klipler_dir)}")
            print("=" * 65 + "\n")
            return True


def start_flow_generation(project_name: str) -> bool:
    bot = FlowBot()
    return asyncio.run(bot.run_project(project_name))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Google Flow Klip Otomasyonu")
    parser.add_argument("--project", type=str, required=True, help="Proje adı")
    args = parser.parse_args()

    ok = start_flow_generation(args.project)
    sys.exit(0 if ok else 1)
