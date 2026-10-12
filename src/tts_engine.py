"""
Çoklu Seslendirme Motoru (Google TTS & Edge-TTS).
Sıfır maliyet ve sıfır API anahtarı ile çalışır.
"""

import asyncio
import os
import re
import subprocess
from typing import List, Dict, Any, Optional
from gtts import gTTS

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"


class TTSEngine:
    def __init__(self, engine_preference: str = "gtts", default_voice: str = "tr-TR-AhmetNeural"):
        self.engine_preference = engine_preference
        self.default_voice = default_voice

    def generate_male(
        self,
        text: str,
        output_audio_path: str
    ) -> Dict[str, Any]:
        """Doğal Türkçe erkek seslendirmesi üretir (tok ve net anlatıcı tonu)."""
        raw_temp = output_audio_path + ".raw.mp3"
        os.makedirs(os.path.dirname(os.path.abspath(output_audio_path)), exist_ok=True)
        
        tts = gTTS(text=text, lang="tr", slow=False)
        tts.save(raw_temp)

        # FFmpeg ile tonu erkek spiker frekansına (asetrate 0.82) çek ve bas güçlendir
        filter_str = "asetrate=24000*0.82,atempo=1.22,equalizer=f=120:width_type=o:width=1.5:g=4,equalizer=f=2800:width_type=o:width=1.5:g=2"
        cmd = [FFMPEG_BIN, "-y", "-i", raw_temp, "-af", filter_str, output_audio_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(raw_temp):
            try:
                os.remove(raw_temp)
            except Exception:
                pass

        # Süreyi hesapla
        duration = 5.0
        try:
            res = subprocess.run([FFMPEG_BIN, "-i", output_audio_path], stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
            match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
            if match:
                h, m, s = match.groups()
                duration = int(h) * 3600 + int(m) * 60 + float(s)
            else:
                duration = max(2.0, len(text) * 0.075)
        except Exception:
            duration = max(2.0, len(text) * 0.075)

        words = text.strip().split()
        total_chars = max(1, sum(len(w) for w in words))
        word_timings = []
        curr_time = 0.0

        for w in words:
            w_duration = (len(w) / total_chars) * duration
            word_timings.append({
                "text": w,
                "start": round(curr_time, 2),
                "end": round(curr_time + w_duration, 2),
                "duration": round(w_duration, 2)
            })
            curr_time += w_duration

        return {
            "engine": "gTTS_Male_Engine",
            "audio_path": output_audio_path,
            "words": word_timings,
            "duration": duration
        }

    async def _try_edge_tts(
        self,
        text: str,
        output_audio_path: str,
        voice: str,
        output_subtitles_path: Optional[str] = None
    ) -> Dict[str, Any]:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        sub_maker = edge_tts.SubMaker()
        audio_bytes = bytearray()
        word_timings = []

        async def fetch():
            nonlocal audio_bytes, word_timings
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes.extend(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    sub_maker.feed(chunk)
                    offset_sec = chunk["offset"] / 10_000_000.0
                    duration_sec = chunk["duration"] / 10_000_000.0
                    word_timings.append({
                        "text": chunk["text"],
                        "start": offset_sec,
                        "end": offset_sec + duration_sec,
                        "duration": duration_sec
                    })

        # 4 saniye zaman aşımı
        await asyncio.wait_for(fetch(), timeout=4.0)

        if not audio_bytes:
            raise RuntimeError("Edge-TTS veri alamadı.")

        os.makedirs(os.path.dirname(os.path.abspath(output_audio_path)), exist_ok=True)
        with open(output_audio_path, "wb") as f:
            f.write(audio_bytes)

        if output_subtitles_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_subtitles_path)), exist_ok=True)
            with open(output_subtitles_path, "w", encoding="utf-8") as f:
                f.write(sub_maker.get_srt())

        return {
            "engine": "edge-tts",
            "audio_path": output_audio_path,
            "subtitles_path": output_subtitles_path,
            "words": word_timings,
            "voice": voice
        }

    def generate(
        self,
        text: str,
        output_audio_path: str,
        voice: Optional[str] = None,
        output_subtitles_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Seslendirmeyi üretir."""
        if self.engine_preference == "edge-tts":
            target_voice = voice or self.default_voice
            try:
                return asyncio.run(self._try_edge_tts(text, output_audio_path, target_voice, output_subtitles_path))
            except Exception as e:
                print(f"  [UYARI] Edge-TTS zaman aşımı ({e}), Google TTS (gTTS) ile devam ediliyor...")
                return self._generate_gtts(text, output_audio_path, output_subtitles_path)
        else:
            return self._generate_gtts(text, output_audio_path, output_subtitles_path)


if __name__ == "__main__":
    engine = TTSEngine(engine_preference="gtts")
    res = engine.generate("Yapay zeka nasıl bulundu? Alan Turing 1950 yılında ilk adımı attı.", "test_speech.mp3")
    print("TTS Başarılı! Oluşan kelime sayısı:", len(res["words"]), "Süre:", res["words"][-1]["end"])
