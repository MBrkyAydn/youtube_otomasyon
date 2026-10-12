"""
Content Architect Engine (İçerik İskeleti & Hiper-Gerçekçilik Motoru).
YouTube Shorts ve Uzun Belgeseller için:
- Sahne sürekliliği ve Master Visual Anchor (Çapa) yönetimi
- Anti-animasyon ve fotorealist sinematik prompt üretimi
- %100 Türkçe garantili dual-stream Veo/Omni seslendirme promptları
- 5-6 sahneli Shorts ve 70 sahneli Long video dramatik iskeleti
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class ContentArchitect:
    def __init__(
        self,
        skeletons_path: str = "config/narrative_skeletons.json",
        styles_path: str = "config/visual_styles.json",
        config_path: str = "config/config.json"
    ):
        self.skeletons_path = skeletons_path
        self.styles_path = styles_path
        self.config_path = config_path

        self.skeletons = self._load_json(skeletons_path)
        self.styles = self._load_json(styles_path)
        self.config = self._load_json(config_path)

        self.anti_animation = self.styles.get(
            "anti_animation_negative_tokens",
            "ABSOLUTELY NO animation, NO 3D render, NO CGI, NO cartoon, NO anime, NO illustration, NO drawing, NO fake textures"
        )

    def _load_json(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def detect_style_preset(self, topic: str) -> str:
        """Konu başlığına göre en uygun görsel stil presetini belirler."""
        t_lower = topic.lower()
        if any(w in t_lower for w in ["tarih", "imparatorluk", "roma", "osmanlı", "savaş", "antik", "yüzyıl", "firavun"]):
            return "historical_documentary"
        elif any(w in t_lower for w in ["yapay zeka", "robot", "uzay", "kuantum", "teknoloji", "gelecek", "bilim", "fizik", "evren"]):
            return "science_technology"
        else:
            return "wildlife_documentary"

    def build_master_anchor(
        self,
        topic: str,
        style_preset: Optional[str] = None,
        subject_override: str = "",
        environment_override: str = ""
    ) -> Dict[str, str]:
        """
        Projenin tamamında görsel tutarlılığı sağlayacak 'Master Visual Anchor' (Ana Çapa) oluşturur.
        Bu çapa tüm 5 (Shorts) veya 70 (Long) sahnenin görsel DNA'sını oluşturur.
        """
        if not style_preset or style_preset not in self.styles.get("presets", {}):
            style_preset = self.detect_style_preset(topic)

        preset_data = self.styles.get("presets", {}).get(style_preset, {})
        t_lower = topic.lower()

        # Konuya göre ana özne ve ortam tespiti
        subject = subject_override
        environment = environment_override

        if not subject:
            if "fil" in t_lower:
                subject = "A massive wild mature African bull elephant with weathered dark-grey wrinkled skin and authentic ivory tusks"
                if not environment:
                    environment = "Arid African savannah with dry cracked earth, scattered acacia trees, and heat haze"
            elif "aslan" in t_lower or "lion" in t_lower:
                subject = "A majestic mature wild male lion with thick dark mane and muscular build"
                if not environment:
                    environment = "Golden African grassland plains during late afternoon sunlight"
            elif "uzay" in t_lower or "gezegen" in t_lower:
                subject = "The colossal celestial planet with swirling atmospheric clouds and glowing rings"
                if not environment:
                    environment = "Deep outer space surrounded by realistic distant star clusters and nebula luminescence"
            elif "yapay zeka" in t_lower or "turing" in t_lower:
                subject = "A brilliant 1950s mathematician in vintage attire surrounded by analog electromechanical computing hardware"
                if not environment:
                    environment = "A moody vintage research laboratory with blackboard calculations and warm amber illumination"
            else:
                # Genel sinematik özne
                subject = f"The authentic real-life central subject representing: {topic}"
                if not environment:
                    environment = "Authentic natural real-world environment with organic atmospheric depth"

        return {
            "style_name": style_preset,
            "subject": subject,
            "environment": environment,
            "cinematography": preset_data.get("cinematography", "Live-action 35mm Arri cinema footage, photorealistic RAW"),
            "lighting": preset_data.get("lighting", "natural cinematic lighting with true optical depth"),
            "textures": preset_data.get("textures", "hyperrealistic organic physical textures"),
            "grading": preset_data.get("grading", "natural documentary color grading"),
            "anti_animation": self.anti_animation
        }

    def clean_dialogue(self, dialogue: str) -> str:
        """Diyalog metnini temizler, tırnakları ve gereksiz karakterleri kaldırır."""
        cleaned = dialogue.replace('"', '').replace('“', '').replace('”', '').strip()
        # Çift boşlukları temizle
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned

    def optimize_dialogue_for_clip_duration(self, dialogue: str, max_words: int = 12) -> Tuple[str, Optional[str]]:
        """
        Flow'un 5-8 saniyelik klip sınırına göre diyaloğun kelime sayısını denetler.
        12 kelimeden uzun diyaloglar klip süresini aşıp sessizlik yaratabileceği için
        cümleyi anlamlı bir noktadan ikiye böler veya düzenler.
        Dönüş: (ilk_parca, varsa_ikinci_parca)
        """
        words = dialogue.strip().split()
        if len(words) <= max_words:
            return dialogue, None

        # Cümleyi noktalama veya bağlaçlardan böl
        split_candidates = [",", ";", "fakat", "ancak", "çünkü", "ve", "bu yüzden", "yani"]
        for cand in split_candidates:
            if cand in dialogue:
                parts = dialogue.split(cand, 1)
                left = parts[0].strip() + ("," if cand in [",", ";"] else "")
                right = (cand + " " + parts[1]).strip() if cand not in [",", ";"] else parts[1].strip()
                if 3 <= len(left.split()) <= max_words:
                    return left, right

        # Mecburi kelime sayısı bölmesi
        left = " ".join(words[:max_words])
        right = " ".join(words[max_words:])
        return left, right

    def format_prompt(
        self,
        action: str,
        dialogue: str,
        camera_shot: str,
        camera_motion: str,
        anchor: Dict[str, str],
        mode: str = "shorts"
    ) -> str:
        """
        Google Flow (Veo / Omni) için kesin çalışan, animasyonu engelleyen ve
        %100 Türkçe seslendirme garantisi sunan hibrit prompt formatlar.
        """
        aspect_ratio = "9:16 vertical" if mode.lower() == "shorts" else "16:9 horizontal"
        clean_dia = self.clean_dialogue(dialogue)

        # 1. VISUAL PROMPT (Tamamen İngilizce & Sinematik Detaylar)
        visual_chunk = (
            f"Live-action cinema documentary shot, {camera_shot}, {camera_motion}. "
            f"{anchor['subject']}, {action}. "
            f"Environment: {anchor['environment']}. "
            f"{anchor['lighting']}. {anchor['cinematography']}, {anchor['textures']}, {anchor['grading']}, "
            f"photorealistic 8k resolution, aspect ratio {aspect_ratio}. "
            f"{anchor['anti_animation']}."
        )

        # 2. AUDIO PROMPT (Kesin Türkçe Direktifi & Süre Sınırı)
        audio_chunk = (
            f"A mature Turkish male documentary narrator with a deep, authoritative, resonant voice speaks clearly in native Turkish: \"{clean_dia}\". "
            f"Flawless Turkish pronunciation, crystal clear studio recording, natural ambient environmental sound effects, zero English speech, no background music, no silence."
        )

        # Birleşik Prompt
        full_prompt = f"{visual_chunk} {audio_chunk}"
        return full_prompt

    def is_clean_english_prompt(self, text: str) -> bool:
        """Metnin temiz bir İngilizce görsel prompt olup olmadığını denetler."""
        if not text or len(text.strip()) < 5:
            return False
        # Türkçe karakterler veya genel Türkçe kelimeler varsa İngilizce değildir
        turkish_chars = set("çğıöşüÇĞİÖŞÜ")
        if any(c in turkish_chars for c in text):
            return False
        turkish_words = ["bir", "ve", "ile", "için", "nasıl", "gibi", "suyu", "hortum", "sahne", "görsel", "cinematic detailed shot"]
        text_lower = text.lower()
        if any(w in text_lower for w in turkish_words):
            return False
        return True

    def generate_shorts_skeleton(
        self,
        topic: str,
        script_scenes: Optional[List[Dict[str, str]]] = None,
        style_preset: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        YouTube Shorts için 5 sahneli dramatik kanca & mekanizma iskeletini üretir.
        Kullanıcı senaryo vermişse o senaryodaki metinleri iskelet adımlarına hizalar.
        """
        anchor = self.build_master_anchor(topic, style_preset=style_preset)
        shorts_def = self.skeletons.get("skeletons", {}).get("shorts", {}).get("structure", [])

        # Varsayılan eylem ve kamera zinciri (Shorts için akıcı geçiş)
        default_actions = [
            ("approaching the riverbank with imposing steady steps, creating subtle dust clouds", "slow cinematic push-in"),
            ("standing near the water's edge, lowering its heavy trunk gracefully toward the surface", "smooth camera pan"),
            ("submerging the trunk tip into crystal clear water, vacuuming eight liters in real time with dynamic fluid motion", "macro focus pull"),
            ("curling its strong trunk upwards towards its open mouth, releasing the rushing water stream directly into throat", "cinematic tracking shot"),
            ("standing proudly against the warm setting sun, water droplets glistening on textured skin", "epic wide cinematic pull back")
        ]

        result_scenes = []
        for idx in range(5):
            stage_meta = shorts_def[idx] if idx < len(shorts_def) else {}
            camera_shot = stage_meta.get("camera_shot", "Cinematic medium tracking shot")
            camera_motion = stage_meta.get("camera_motion", "slow cinematic movement")

            # Diyalog ve Aksiyon belirleme
            if script_scenes and idx < len(script_scenes):
                raw_item = script_scenes[idx]
                dialogue = raw_item.get("dialogue", stage_meta.get("dialogue_example", ""))
                custom_visual = raw_item.get("visual", "").strip()
                action = custom_visual if self.is_clean_english_prompt(custom_visual) else default_actions[idx][0]
                motion = raw_item.get("motion", camera_motion)
            else:
                dialogue = stage_meta.get("dialogue_example", f"{topic} hakkında bilinmeyen büyüleyici gerçek.")
                action = default_actions[idx][0]
                motion = default_actions[idx][1]

            # Süre optimizasyonu (Max 12 kelime)
            dialogue, _ = self.optimize_dialogue_for_clip_duration(dialogue, max_words=stage_meta.get("max_words", 11))

            flow_prompt = self.format_prompt(
                action=action,
                dialogue=dialogue,
                camera_shot=camera_shot,
                camera_motion=motion,
                anchor=anchor,
                mode="shorts"
            )

            result_scenes.append({
                "id": idx + 1,
                "phase": stage_meta.get("phase", f"scene_{idx + 1}"),
                "phase_name": stage_meta.get("name", f"Sahne {idx + 1}"),
                "dialogue": dialogue,
                "action": action,
                "camera_shot": camera_shot,
                "camera_motion": motion,
                "flow_prompt": flow_prompt,
                "clip_filename": f"scene_{idx + 1}.mp4"
            })

        return result_scenes

    def generate_long_skeleton(
        self,
        topic: str,
        script_scenes: Optional[List[Dict[str, str]]] = None,
        style_preset: Optional[str] = None,
        target_scene_count: int = 70
    ) -> List[Dict[str, Any]]:
        """
        Uzun Belgesel (10-12 Dakika) için 6 bölümlü, 70 sahneli dramatik iskelet üretir.
        Her bölümün tematik ışığı, kamera açıları ve anlatım derinliği birbirine zincirlenir.
        """
        anchor = self.build_master_anchor(topic, style_preset=style_preset)
        long_def = self.skeletons.get("skeletons", {}).get("long_documentary", {})
        chapters = long_def.get("chapters", [])

        # Sahne tipleri ve hareket paleti
        shot_palette = [
            "Cinematic wide establishing shot",
            "Medium tracking shot following physical movement",
            "Intense close-up focusing with optical depth on facial features",
            "Extreme macro close-up revealing microscopic texture and fluid dynamics",
            "Over-the-shoulder action perspective framing real-time physics",
            "Low-angle cinematic hero shot capturing immense scale",
            "Slow epic pull-back camera motion to horizon"
        ]

        motion_palette = [
            "slow cinematic push-in",
            "smooth lateral tracking pan",
            "slow downward crane drift",
            "macro optical focus pull",
            "dynamic tracking following subject",
            "epic wide cinematic pull back",
            "subtle handheld documentary stabilization"
        ]

        chapter_actions = {
            1: [
                "standing majestically in the distance as morning mist rises over the landscape",
                "turning slowly toward camera, eyes alive with intelligence and quiet authority",
                "taking deliberate heavy footsteps across the terrain, raising soft plumes of dust",
                "pausing at the edge of the clearing, scanning the vast horizon with deep awareness",
                "raising head slowly to catch the wind direction, showing authentic muscular tension",
                "interacting gently with the natural elements, demonstrating innate curiosity",
                "moving in steady rhythmic harmony across the atmospheric landscape",
                "framed against dramatic low-angle sunlight, establishing cinematic scale"
            ],
            2: [
                "navigating ancient migration pathways worn smooth over thousands of years",
                "navigating challenging rocky terrain, displaying deep evolutionary adaptations",
                "weathering sudden ambient wind gusts, textured skin catching dynamic light",
                "interacting with historical terrain landmarks, demonstrating ancestral memory",
                "moving deliberately through changing topography under intense daylight",
                "pausing beside ancient geological formations, rooted deeply in nature"
            ],
            3: [
                "lowering sensitive trunk tip into pristine water with fluid ripple dynamics",
                "macro optical lens capturing fine muscular contractions of the siphon mechanism",
                "vacuuming gallons of fresh water with clear, dynamic fluid suction",
                "curling trunk upward with athletic precision, sealing internal chambers",
                "releasing water torrent directly into throat, glistening droplets in raw light",
                "repeating the hydration sequence with calm, rhythmic biological mastery"
            ],
            4: [
                "enduring arid drought conditions with unyielding physical resilience",
                "excavating dry sandy riverbed with forefeet to reach hidden groundwater",
                "shielding fellow herd members with massive frame against harsh elements",
                "standing firm during a passing dust storm, textured skin coated in fine earth",
                "demonstrating intense social bond and communication during times of stress"
            ],
            5: [
                "dispersing vital forest seeds and opening pathways for countless other species",
                "sharing natural water reservoirs peacefully with ambient birds and small wildlife",
                "shaping the fertile ecosystem landscape as a quintessential keystone species",
                "interacting harmoniously with the surrounding biodiversity under soft twilight"
            ],
            6: [
                "walking gracefully toward the boundless golden sunset horizon",
                "standing atop an elevated ridge overlooking the vast panorama in quiet triumph",
                "releasing a gentle final spray of water into the glowing evening sky",
                "silhouetted against the majestic dusk, leaving a lasting impression of natural wonder"
            ]
        }

        total_scenes = max(len(script_scenes) if script_scenes else 0, target_scene_count)
        result_scenes = []

        for idx in range(total_scenes):
            scene_num = idx + 1

            # Hangi bölüme denk geliyor?
            current_chapter = None
            for ch in chapters:
                start, end = ch["scene_range"]
                if start <= scene_num <= end:
                    current_chapter = ch
                    break
            if not current_chapter:
                current_chapter = chapters[-1] if chapters else {"title": "Belgesel Akışı", "chapter_id": 6}

            ch_id = current_chapter.get("chapter_id", 1)
            actions_pool = chapter_actions.get(ch_id, chapter_actions[1])
            default_action = actions_pool[(scene_num - 1) % len(actions_pool)]

            camera_shot = shot_palette[idx % len(shot_palette)]
            camera_motion = motion_palette[idx % len(motion_palette)]

            if script_scenes and idx < len(script_scenes):
                raw_item = script_scenes[idx]
                dialogue = raw_item.get("dialogue", "")
                custom_visual = raw_item.get("visual", "").strip()
                action = custom_visual if self.is_clean_english_prompt(custom_visual) else default_action
                motion = raw_item.get("motion", camera_motion)
            else:
                dialogue = f"{topic} konusunun {current_chapter.get('title', '')} kapsamındaki derin bilimsel detayları."
                action = default_action
                motion = camera_motion

            # Süre denetimi (Uzun videoda da klip başına max 12 kelime)
            dialogue, _ = self.optimize_dialogue_for_clip_duration(dialogue, max_words=12)

            flow_prompt = self.format_prompt(
                action=action,
                dialogue=dialogue,
                camera_shot=camera_shot,
                camera_motion=motion,
                anchor=anchor,
                mode="long"
            )

            result_scenes.append({
                "id": scene_num,
                "chapter_id": ch_id,
                "chapter_title": current_chapter.get("title", ""),
                "dialogue": dialogue,
                "action": action,
                "camera_shot": camera_shot,
                "camera_motion": motion,
                "flow_prompt": flow_prompt,
                "clip_filename": f"scene_{scene_num}.mp4"
            })

        return result_scenes
