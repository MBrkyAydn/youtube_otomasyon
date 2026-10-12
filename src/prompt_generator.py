"""
Google Flow (Veo & Omni) Prompt ve Sahne Üretici.
ContentArchitect mimarisi ile entegre çalışır:
- Master Visual Anchor (Görsel Tutarlılık Çapası)
- Anti-animasyon fotorealist sinematografi kuralları
- Kesin Türkçe seslendirme ve süre denetimli promptlar
- Shorts (5 sahne) ve Uzun Belgesel (70 sahneye kadar) dramatik iskeletleri
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.content_architect import ContentArchitect


class PromptGenerator:
    def __init__(
        self,
        skeleton_path: str = "config/prompt_skeleton.json",
        config_path: str = "config/config.json"
    ):
        self.skeleton_path = skeleton_path
        self.config_path = config_path
        self.architect = ContentArchitect(config_path=config_path)

    def format_flow_prompt(
        self,
        scene_visual: str,
        dialogue: str,
        mode: str = "shorts",
        camera_motion: str = "slow cinematic push-in",
        topic: str = "Doğa Belgeseli"
    ) -> str:
        """
        Google Flow (Veo / Omni) için görsel ve garantili Türkçe seslendirme promptunu formatlar.
        ContentArchitect motorunu kullanarak hiper-gerçekçi ve animasyon önleyici prompt üretir.
        """
        anchor = self.architect.build_master_anchor(topic)
        return self.architect.format_prompt(
            action=scene_visual,
            dialogue=dialogue,
            camera_shot="Cinematic documentary shot",
            camera_motion=camera_motion,
            anchor=anchor,
            mode=mode
        )

    def create_project(
        self,
        project_name: str,
        title: str,
        scenes: Optional[List[Dict[str, str]]] = None,
        mode: str = "shorts",
        style_preset: Optional[str] = None,
        target_scenes: int = 70,
        tags: Optional[List[str]] = None,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Yeni bir video projesi oluşturur ve ContentArchitect ile profesyonel promptları kaydeder.
        Shorts modunda 5 sahneli viral iskelet, Long modunda 70 sahneli 6 bölümlü belgesel üretir.
        """
        project_dir = os.path.join("projects", project_name)
        klipler_dir = os.path.join(project_dir, "klipler")
        os.makedirs(klipler_dir, exist_ok=True)

        anchor = self.architect.build_master_anchor(title, style_preset=style_preset)

        # Sahne listesini ContentArchitect ile iskelete oturt
        if mode.lower() == "shorts":
            architect_scenes = self.architect.generate_shorts_skeleton(
                topic=title,
                script_scenes=scenes,
                style_preset=style_preset
            )
        else:
            architect_scenes = self.architect.generate_long_skeleton(
                topic=title,
                script_scenes=scenes,
                style_preset=style_preset,
                target_scene_count=target_scenes
            )

        prompts_txt_lines = [
            "=" * 70,
            f"   🎬 PROJE: {title.upper()}",
            f"   📐 FORMAT: {'9:16 Dikey Shorts' if mode == 'shorts' else '16:9 Yatay Video'}",
            f"   🎞️ TOPLAM SAHNE: {len(architect_scenes)}",
            f"   🎨 GÖRSEL STİL: {anchor['style_name']}",
            "=" * 70,
            "\n[MASTER VISUAL ANCHOR (GÖRSEL SÜREKLİLİK ÇAPASI)]",
            f"• Özne: {anchor['subject']}",
            f"• Ortam: {anchor['environment']}",
            f"• Sinematografi: {anchor['cinematography']}",
            f"• Anti-Animasyon Filtresi: AKTİF (Sıfır 3D / Çizgi Film)",
            "\n" + "-" * 70,
            "[KULLANIM KILAVUZU]",
            "1. Chrome'da flow.google.com açın.",
            "2. Aşağıdaki her sahnenin 'FLOW PROMPTU'nu kopyalayıp Flow'a yapıştırın ve üretin.",
            "3. VEYA terminalde 'python main.py flow --project " + project_name + "' komutuyla otomatik indirin.",
            "-" * 70
        ]

        formatted_scenes = []
        for sc in architect_scenes:
            sc_id = sc["id"]
            phase_info = sc.get("phase_name", sc.get("chapter_title", f"Sahne {sc_id}"))

            formatted_scenes.append({
                "id": sc_id,
                "dialogue": sc["dialogue"],
                "visual": sc.get("action", ""),
                "camera_shot": sc.get("camera_shot", ""),
                "camera_motion": sc.get("camera_motion", ""),
                "flow_prompt": sc["flow_prompt"],
                "clip_filename": sc["clip_filename"]
            })

            prompts_txt_lines.append(f"\n🎬 [SAHNE {sc_id}] — {phase_info.upper()}")
            prompts_txt_lines.append(f"📹 Kamera: {sc.get('camera_shot', '')} ({sc.get('camera_motion', '')})")
            prompts_txt_lines.append(f"🗣️ TÜRKÇE DİYALOG:")
            prompts_txt_lines.append(f"\"{sc['dialogue']}\"")
            prompts_txt_lines.append(f"\n✨ GOOGLE FLOW PROMPTU (Hiper-Gerçekçi + Türkçe Ses):")
            prompts_txt_lines.append(sc["flow_prompt"])
            prompts_txt_lines.append("-" * 70)

        project_data = {
            "name": project_name,
            "title": title,
            "description": description or f"{title}\n\n#belgesel #{mode} #bilim #doğa",
            "tags": tags or ["belgesel", mode, "türkçe", "bilim"],
            "mode": mode,
            "master_anchor": anchor,
            "scenes": formatted_scenes
        }

        # project.json kaydet
        json_path = os.path.join(project_dir, "project.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)

        # google_flow_prompts.txt kaydet
        txt_path = os.path.join(project_dir, "google_flow_prompts.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(prompts_txt_lines))

        print(f"[OK] Proje oluşturuldu: {project_dir}")
        print(f"[OK] Master Visual Anchor oluşturuldu: {anchor['subject'][:50]}...")
        print(f"[OK] Google Flow promptları hazırlandı ({len(formatted_scenes)} sahne): {txt_path}")
        return project_data

    def parse_script_file(self, file_path: str, mode: str = "shorts") -> List[Dict[str, str]]:
        """
        senaryo.txt dosyasını okuyup sahne listesine dönüştürür.
        Formatlar:
          1) 1 | Diyalog metni | Görsel açıklaması (isteğe bağlı)
          2) Diyalog metni
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Senaryo dosyası bulunamadı: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

        default_motions = [
            "slow cinematic push-in",
            "smooth lateral camera pan",
            "macro optical focus pull",
            "cinematic slow motion tracking shot",
            "epic wide cinematic pull back"
        ]

        scenes = []
        for idx, line in enumerate(lines, 1):
            parts = [p.strip() for p in line.split("|")]

            dialogue = ""
            visual = ""
            motion = default_motions[(idx - 1) % len(default_motions)]

            if len(parts) >= 3:
                dialogue = parts[1]
                visual = parts[2]
            elif len(parts) == 2:
                if parts[0].isdigit() or parts[0].lower().startswith("sahne"):
                    dialogue = parts[1]
                else:
                    dialogue = parts[0]
                    visual = parts[1]
            else:
                raw_text = parts[0]
                cleaned = re.sub(r"^(\d+[\.\)\|\:\-]?\s*|(sahne\s*\d+[\:\-]?\s*))", "", raw_text, flags=re.IGNORECASE)
                dialogue = cleaned.strip()

            if not visual:
                visual = ""

            scenes.append({
                "dialogue": dialogue,
                "visual": visual,
                "motion": motion
            })

        return scenes
