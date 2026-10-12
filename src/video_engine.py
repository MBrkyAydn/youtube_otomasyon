"""
Video Kurgu ve Render Motoru.
Google Flow'dan (Veo) indirilen sesli video kliplerini (scene_1.mp4, scene_2.mp4...)
kusursuz şekilde birleştirir, dinamik altyazı ve arka plan müziği ekler.
"""

import os
import shutil
import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import imageio_ffmpeg
    DEFAULT_FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    DEFAULT_FFMPEG = shutil.which("ffmpeg") or "ffmpeg"


class VideoEngine:
    def __init__(self, ffmpeg_bin: Optional[str] = None):
        self.ffmpeg_bin = ffmpeg_bin or DEFAULT_FFMPEG
        if not self.ffmpeg_bin:
            raise RuntimeError("FFmpeg çalıştırılabilir dosyası bulunamadı!")

    def get_clip_duration(self, file_path: str) -> float:
        """Video veya ses dosyasının süresini saniye cinsinden döndürür."""
        cmd = [self.ffmpeg_bin, "-i", str(file_path)]
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, encoding="utf-8", errors="ignore")
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if match:
            hours, minutes, seconds = match.groups()
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        return 5.0

    def _escape_filter_path(self, path: str) -> str:
        """FFmpeg filtre parametreleri için dosya yolunu güvenli hale getirir."""
        clean_path = os.path.abspath(path).replace("\\", "/")
        clean_path = clean_path.replace(":", "\\:")
        return clean_path

    def normalize_clip(
        self,
        input_clip_path: str,
        output_clip_path: str,
        target_w: int,
        target_h: int,
        fps: int = 30
    ) -> str:
        """
        Google Flow'dan gelen herhangi bir video klibini standart çözünürlük,
        fps ve 48kHz stereo ses formatına dönüştürür.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_clip_path)), exist_ok=True)

        # Orantıyı koruyarak kırp ve doldur (scale + crop)
        filter_str = (
            f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
            f"crop={target_w}:{target_h},"
            f"fps={fps},format=yuv420p"
        )

        duration = self.get_clip_duration(input_clip_path)
        audio_filters = ["aresample=48000"]
        if duration > 0.4:
            fade_dur = min(0.15, duration / 4)
            audio_filters.append(f"afade=t=in:st=0:d={fade_dur:.2f}")
            audio_filters.append(f"afade=t=out:st={duration - fade_dur:.2f}:d={fade_dur:.2f}")

        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-i", str(input_clip_path),
            "-vf", filter_str,
            "-af", ",".join(audio_filters),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-c:a", "aac",
            "-ar", "48000",
            "-ac", "2",
            "-b:a", "192k",
            str(output_clip_path)
        ]

        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
        if res.returncode != 0:
            raise RuntimeError(f"Klip normalizasyon hatası ({input_clip_path}): {res.stderr[-300:]}")

        return output_clip_path

    def assemble_flow_clips(
        self,
        clip_paths: List[str],
        output_video_path: str,
        target_w: int = 1080,
        target_h: int = 1920,
        background_music_path: Optional[str] = None,
        narration_audio_path: Optional[str] = None,
        subtitles_ass_path: Optional[str] = None,
        bg_music_volume: float = 0.08,
        fps: int = 30
    ) -> str:
        """
        Google Flow sesli video kliplerini birleştirir, arka plan müziği ekler ve altyazıyı gömer.
        """
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(output_video_path)), "temp_work")
        os.makedirs(temp_dir, exist_ok=True)

        normalized_clips = []
        for idx, clip in enumerate(clip_paths, 1):
            norm_path = os.path.join(temp_dir, f"norm_clip_{idx}.mp4")
            self.normalize_clip(clip, norm_path, target_w, target_h, fps=fps)
            normalized_clips.append(norm_path)

        # 1. Klipleri birleştir (concat listesi)
        concat_txt = os.path.join(temp_dir, "concat_clips.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for c in normalized_clips:
                clean_p = os.path.abspath(c).replace("\\", "/")
                f.write(f"file '{clean_p}'\n")

        merged_raw = os.path.join(temp_dir, "merged_raw.mp4")
        cmd_concat = [
            self.ffmpeg_bin,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_txt,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            "-ac", "2",
            "-af", "aresample=async=1000",
            merged_raw
        ]
        res = subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg concat hatası: {res.stderr[-300:]}")

        total_duration = self.get_clip_duration(merged_raw)
        fade_out_start = max(0.0, total_duration - 1.5)
        fade_out_dur = min(1.5, total_duration)

        # 2. Seslendirme (TTS), Müzik ve Altyazı Ekleme
        has_narration = narration_audio_path and os.path.exists(narration_audio_path)
        has_music = background_music_path and os.path.exists(background_music_path)
        has_subs = subtitles_ass_path and os.path.exists(subtitles_ass_path)

        final_cmd = [self.ffmpeg_bin, "-y", "-i", merged_raw]

        input_index = 1
        narr_idx = None
        music_idx = None

        if has_narration:
            final_cmd.extend(["-i", str(narration_audio_path)])
            narr_idx = input_index
            input_index += 1

        if has_music:
            final_cmd.extend(["-stream_loop", "-1", "-i", str(background_music_path)])
            music_idx = input_index
            input_index += 1

        filter_parts_v = []
        filter_parts_a = []

        if has_subs:
            escaped_sub = self._escape_filter_path(subtitles_ass_path)
            filter_parts_v.append(f"ass='{escaped_sub}'")

        if has_narration and has_music:
            filter_parts_a.append(
                f"[0:a]volume=0.20,aresample=48000[amb];"
                f"[{narr_idx}:a]volume=1.05,aresample=48000[spk];"
                f"[{music_idx}:a]atrim=0:{total_duration:.2f},afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_start:.2f}:d={fade_out_dur:.2f},volume={bg_music_volume:.2f},aresample=48000[bg_loop];"
                f"[spk][amb][bg_loop]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[a_out]"
            )
        elif has_narration:
            filter_parts_a.append(
                f"[0:a]volume=0.20,aresample=48000[amb];"
                f"[{narr_idx}:a]volume=1.05,aresample=48000[spk];"
                f"[spk][amb]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a_out]"
            )
        elif has_music:
            filter_parts_a.append(
                f"[{music_idx}:a]atrim=0:{total_duration:.2f},afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_start:.2f}:d={fade_out_dur:.2f},volume={bg_music_volume:.2f},aresample=48000[bg_loop];"
                f"[0:a]volume=1.0,aresample=48000[orig_audio];"
                f"[orig_audio][bg_loop]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a_out]"
            )

        maps = []
        if filter_parts_v and filter_parts_a:
            filter_complex_str = f"[0:v]{','.join(filter_parts_v)}[v_out];" + ";".join(filter_parts_a)
            maps = ["-map", "[v_out]", "-map", "[a_out]"]
        elif filter_parts_v:
            filter_complex_str = f"[0:v]{','.join(filter_parts_v)}[v_out]"
            maps = ["-map", "[v_out]", "-map", "0:a"]
        elif filter_parts_a:
            filter_complex_str = ";".join(filter_parts_a)
            maps = ["-map", "0:v", "-map", "[a_out]"]
        else:
            shutil.copy2(merged_raw, output_video_path)
            shutil.rmtree(temp_dir, ignore_errors=True)
            return output_video_path

        final_cmd.extend([
            "-filter_complex", filter_complex_str,
            *maps,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            str(output_video_path)
        ])

        res_final = subprocess.run(final_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
        if res_final.returncode != 0:
            raise RuntimeError(f"FFmpeg final render hatası: {res_final.stderr[-400:]}")

        # Geçici dosyaları temizle
        shutil.rmtree(temp_dir, ignore_errors=True)
        return output_video_path


if __name__ == "__main__":
    ve = VideoEngine()
    print("VideoEngine hazır, FFmpeg:", ve.ffmpeg_bin)
