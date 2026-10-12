"""
Dinamik Altyazı Motoru (ASS ve SRT Formatları).
YouTube Shorts (ortalanmış, kalın, yüksek görünürlük) ve Uzun Video (alt bant, sinematik)
için stilize edilmiş altyazılar üretir.
"""

import os
from typing import List, Dict, Any, Optional


class SubtitleEngine:
    def __init__(self):
        pass

    @staticmethod
    def format_timestamp_ass(seconds: float) -> str:
        """Saniyeyi ASS zaman formatına (H:MM:SS.cs) çevirir."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int(round((seconds - int(seconds)) * 100))
        if centisecs >= 100:
            centisecs = 99
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

    @staticmethod
    def format_timestamp_srt(seconds: float) -> str:
        """Saniyeyi SRT zaman formatına (HH:MM:SS,mmm) çevirir."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds - int(seconds)) * 1000))
        if millis >= 1000:
            millis = 999
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def generate_ass(
        self,
        words_or_segments: List[Dict[str, Any]],
        output_path: str,
        mode: str = "shorts",
        font_name: str = "Arial"
    ) -> str:
        """
        Gelişmiş stillere sahip ASS altyazı dosyası üretir.
        mode: 'shorts' veya 'long'
        """
        is_shorts = (mode.lower() == "shorts")

        if is_shorts:
            # Shorts: Ekranın ortasına yakın, kalın, büyük font, sarı/beyaz ve siyah kontur
            font_size = 46
            margin_v = 450  # Shorts alt butonlarına (beğen, yorum vb.) denk gelmemesi için yukarıda
            primary_color = "&H0000FFFF"  # Sarı (&HBBGGRR formatında ASS)
            outline_color = "&H00000000"  # Siyah kontur
            bold = -1  # ASS'de -1 true demektir
            outline = 4
            shadow = 2
        else:
            # Uzun video: Alt bant, şık ve sinematik
            font_size = 28
            margin_v = 70
            primary_color = "&H00FFFFFF"  # Beyaz
            outline_color = "&H00000000"
            bold = 0
            outline = 2.5
            shadow = 1.5

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {1080 if is_shorts else 1920}
PlayResY: {1920 if is_shorts else 1080}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},&H000000FF,{outline_color},&H80000000,{bold},0,0,0,100,100,0,0,1,{outline},{shadow},2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        events = []
        # Kelimeleri veya segmentleri gruplayarak ekrana bas
        # Shorts için 2-3 kelimelik hızlı bloklar, Uzun video için 5-7 kelimelik bloklar
        max_words_per_line = 3 if is_shorts else 7

        if words_or_segments and "words" in words_or_segments[0]:
            # Sahne bazlı liste
            all_words = []
            for item in words_or_segments:
                all_words.extend(item.get("words", []))
        else:
            all_words = words_or_segments

        if not all_words:
            # Eğer kelime bazlı zaman yoksa boş döner
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(header)
            return output_path

        # Gruplama
        i = 0
        while i < len(all_words):
            chunk = all_words[i:i + max_words_per_line]
            if not chunk:
                break
            start_time = chunk[0].get("start", 0.0)
            end_time = chunk[-1].get("end", start_time + 1.0)
            text = " ".join([w.get("text", "") for w in chunk]).strip()

            # Türkçe büyük harf kuralı (Shorts'ta büyük harf dikkat çeker)
            if is_shorts:
                text = text.upper()

            start_ass = self.format_timestamp_ass(start_time)
            end_ass = self.format_timestamp_ass(end_time)

            events.append(f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{text}")
            i += len(chunk)

        content = header + "\n".join(events) + "\n"
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return output_path


if __name__ == "__main__":
    engine = SubtitleEngine()
    test_words = [
        {"text": "Yapay", "start": 0.0, "end": 0.4},
        {"text": "zeka", "start": 0.4, "end": 0.8},
        {"text": "nasıl", "start": 0.8, "end": 1.2},
        {"text": "bulundu?", "start": 1.2, "end": 1.7},
        {"text": "Alan", "start": 1.8, "end": 2.2},
        {"text": "Turing", "start": 2.2, "end": 2.6},
        {"text": "1950'de", "start": 2.6, "end": 3.1},
        {"text": "başlattı.", "start": 3.1, "end": 3.6}
    ]
    path = engine.generate_ass(test_words, "test_sub.ass", mode="shorts")
    print(f"ASS altyazı üretildi: {path}")
