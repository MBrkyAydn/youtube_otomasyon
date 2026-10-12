"""
Google Flow (Veo) Prompt ve Diyalog Üretici.
Her sahne için Google Flow'un en iyi anladığı video hareket promptlarını
ve konuşulacak Türkçe diyalogları hazırlar.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


class PromptGenerator:
    def __init__(self, skeleton_path: str = "config/prompt_skeleton.json", config_path: str = "config/config.json"):
        self.skeleton_path = skeleton_path
        self.config_path = config_path
        self.skeleton = self._load_json(skeleton_path)
        self.config = self._load_json(config_path)

    def _load_json(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def format_flow_prompt(
        self,
        scene_visual: str,
        dialogue: str,
        mode: str = "shorts",
        camera_motion: str = "slow cinematic push-in"
    ) -> str:
        """Google Flow (Veo / Omni) için görsel ve Türkçe seslendirme promptunu formatlar."""
        aspect_ratio = "9:16 vertical" if mode.lower() == "shorts" else "16:9 horizontal"
        clean_dialogue = dialogue.replace('"', '').strip()
        clean_visual = scene_visual.strip()

        # Google Flow'un (Veo & Omni) ses motoruna özel resmi Türkçe seslendirme direktifi:
        prompt = (
            f"Cinematic video clip, {camera_motion}, {clean_visual}, photorealistic 8k, aspect ratio {aspect_ratio}. "
            f"A deep, clear Turkish male narrator voiceover speaks clearly in native Turkish: \"{clean_dialogue}\". "
            f"Natural Turkish speech delivery, realistic environmental sound effects, no background music."
        )
        return prompt

    def create_project(
        self,
        project_name: str,
        title: str,
        scenes: List[Dict[str, str]],
        mode: str = "shorts",
        tags: Optional[List[str]] = None,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Yeni bir video projesi oluşturur ve Google Flow video/diyalog promptlarını kaydeder.
        scenes: [ {"dialogue": "...", "visual": "...", "motion": "..."}, ... ]
        """
        project_dir = os.path.join("projects", project_name)
        klipler_dir = os.path.join(project_dir, "klipler")
        os.makedirs(klipler_dir, exist_ok=True)

        formatted_scenes = []
        prompts_txt_lines = [
            "=" * 65,
            f"   PROJE: {title.upper()}",
            f"   FORMAT: {'9:16 Dikey Shorts' if mode == 'shorts' else '16:9 Yatay Video'}",
            "=" * 65,
            "\n[NASIL KULLANILIR?]",
            "1. flow.google.com adresine gidin.",
            "2. Aşağıdaki her sahne için 'Video Promptu'nu yapıştırın ve 'Diyalog' kısmını ekleyin.",
            "3. İndirdiğiniz sesli video kliplerini şu klasöre atın:",
            f"   projects/{project_name}/klipler/\n",
            "   (İsimler: scene_1.mp4, scene_2.mp4, scene_3.mp4...)\n",
            "4. Klipleri attıktan sonra terminalde şu komutu çalıştırın:",
            f"   python main.py build --project {project_name}\n",
            "-" * 65
        ]

        for idx, scene in enumerate(scenes, 1):
            dialogue = scene.get("dialogue", scene.get("voiceover", ""))
            visual = scene.get("visual", "")
            motion = scene.get("motion", "cinematic camera movement")

            flow_prompt = self.format_flow_prompt(visual, dialogue, mode=mode, camera_motion=motion)

            scene_data = {
                "id": idx,
                "dialogue": dialogue,
                "visual": visual,
                "flow_prompt": flow_prompt,
                "clip_filename": f"scene_{idx}.mp4"
            }
            formatted_scenes.append(scene_data)

            prompts_txt_lines.append(f"\n🎬 [SAHNE {idx}]")
            prompts_txt_lines.append(f"🗣️ TÜRKÇE DİYALOG / SESLENDİRME:")
            prompts_txt_lines.append(f"\"{dialogue}\"")
            prompts_txt_lines.append(f"\n✨ GOOGLE FLOW VIDEO PROMPTU:")
            prompts_txt_lines.append(f"{flow_prompt}")
            prompts_txt_lines.append("-" * 50)

        project_data = {
            "name": project_name,
            "title": title,
            "description": description or f"{title}\n\n#shorts #teknoloji #yapayzeka",
            "tags": tags or ["youtube", "shorts", "yapay zeka"],
            "mode": mode,
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
        print(f"[OK] Google Flow promptları hazırlandı: {txt_path}")
        return project_data

    def parse_script_file(self, file_path: str, mode: str = "shorts") -> List[Dict[str, str]]:
        """
        senaryo.txt dosyasını okuyup sahne listesine dönüştürür.
        Desteklenen formatlar:
          1) 1 | Diyalog metni | Görsel açıklaması (isteğe bağlı)
          2) Diyalog metni
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Senaryo dosyası bulunamadı: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

        default_motions = [
            "slow cinematic zoom in",
            "smooth camera pan across the scene",
            "cinematic slow motion tracking shot",
            "close up camera focus",
            "epic wide cinematic pull back"
        ]

        scenes = []
        for idx, line in enumerate(lines, 1):
            parts = [p.strip() for p in line.split("|")]
            
            dialogue = ""
            visual = ""
            motion = default_motions[(idx - 1) % len(default_motions)]

            if len(parts) >= 3:
                # Format: 1 | Diyalog | Görsel
                dialogue = parts[1]
                visual = parts[2]
            elif len(parts) == 2:
                # Format: 1 | Diyalog  VEYA  Diyalog | Görsel
                if parts[0].isdigit() or parts[0].lower().startswith("sahne"):
                    dialogue = parts[1]
                else:
                    dialogue = parts[0]
                    visual = parts[1]
            else:
                # Format: Düz metin (numaralı veya numarasız)
                raw_text = parts[0]
                import re
                cleaned = re.sub(r"^(\d+[\.\)\|\:\-]?\s*|(sahne\s*\d+[\:\-]?\s*))", "", raw_text, flags=re.IGNORECASE)
                dialogue = cleaned.strip()

            if not visual:
                visual = f"Cinematic detailed shot representing: {dialogue}"

            scenes.append({
                "dialogue": dialogue,
                "visual": visual,
                "motion": motion
            })

        return scenes
