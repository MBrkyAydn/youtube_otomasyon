"""
YouTube Otomasyon Ana Yönetim Sistemi (Google Flow Entegreli).
Kullanım:
  1. Yeni Proje & Promptları Oluştur:
     python main.py create --name ilk_video --topic "Yapay Zeka Nasıl Bulundu?" --mode shorts

  2. Flow'dan İndirilen Klipleri Birleştir (Dinamik Altyazı + Müzik):
     python main.py build --project ilk_video

  3. YouTube'a Yükle:
     python main.py upload --project ilk_video --privacy unlisted
"""

import os
import sys
import argparse
import json
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Windows terminal utf-8 ayari
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# src klasörünü yola ekle
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.video_engine import VideoEngine
from src.subtitle_engine import SubtitleEngine
from src.prompt_generator import PromptGenerator
from src.youtube_uploader import YouTubeUploader
from src.flow_bot import start_flow_generation
from src.tts_engine import TTSEngine


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def cmd_create(args):
    """Yeni bir video projesi oluşturur ve Google Flow video/diyalog promptlarını hazırlar."""
    pg = PromptGenerator()
    mode = args.mode or "shorts"
    name = args.name or f"proje_{int(time.time())}"
    topic = args.topic or "Yapay Zeka Nasıl Bulundu?"

    if mode == "shorts":
        # 35-45 saniyelik Shorts (5 sahne)
        default_scenes = [
            {
                "dialogue": "1950 yılında Alan Turing dünyayı sarsan bir soru sordu: Makineler düşünebilir mi?",
                "visual": "A brilliant 1950s vintage mathematician and computer pioneer working on a glowing mechanical computer in a misty British laboratory, intense mood",
                "motion": "slow cinematic zoom in on face"
            },
            {
                "dialogue": "1956'da bir grup bilim insanı toplandı ve tarihte ilk kez 'Yapay Zeka' terimini kullandı.",
                "visual": "1950s scientists in academic hall with a blackboard filled with glowing mathematical equations",
                "motion": "smooth camera pan across the room"
            },
            {
                "dialogue": "Yıllarca süren yapay zeka kışından sonra, derin öğrenme algoritmaları ve süper bilgisayarlar her şeyi değiştirdi.",
                "visual": "Futuristic dark server room with pulsating blue and cyan fiber optic neural network lights",
                "motion": "forward camera track through server racks"
            },
            {
                "dialogue": "Satranç şampiyonlarını yenen, sanat üreten ve kod yazan zekalar artık bir hayal değil.",
                "visual": "Mechanical cybernetic android hand placing a glowing crystal piece on a holographic digital board",
                "motion": "close up camera focus on android hand"
            },
            {
                "dialogue": "Peki sizce yapay zeka insanlığın en büyük kurtarıcısı mı, yoksa en büyük tehdidi mi?",
                "visual": "Silhouette of a visionary looking out at an immense futuristic neon skyline with glowing AI horizon",
                "motion": "epic slow pull back camera shot"
            }
        ]
    else:
        # Uzun video için sahne şablonu (16:9)
        default_scenes = [
            {
                "dialogue": "İnsanlık asırlar boyunca makinelerin sadece fiziksel işler yapabileceğini düşündü. Fakat 20. yüzyılda bu düşünce tamamen yıkıldı.",
                "visual": "Ancient bronze clockwork mechanisms slowly transforming into glowing modern silicon chips",
                "motion": "cinematic macro pan over intricate gears"
            },
            {
                "dialogue": "Alan Turing'in ortaya attığı düşünce deneyi, bir gün insan gibi düşünen ve hisseden zihinlerin doğacağını müjdeliyordu.",
                "visual": "Vintage British computer laboratory with vacuum tubes, dramatic window lighting",
                "motion": "slow push in"
            },
            {
                "dialogue": "1956 Dartmouth Konferansı ile başlayan yolculuk, başlangıçta dev hedeflere sahipti; fakat işlem gücü yetersizliği ilk yapay zeka kışını getirdi.",
                "visual": "Frozen abandoned mainframe room covered in frost and icy mist, moody lighting",
                "motion": "slow cinematic tracking shot"
            },
            {
                "dialogue": "2010'lu yıllarla birlikte büyük veri ve yapay sinir ağları birleştiğinde, insan beynini taklit eden modeller patlama yaptı.",
                "visual": "Hyper-realistic pulsating 3D neural web network visualization, cosmic backdrop",
                "motion": "continuous forward flight through neural pathways"
            },
            {
                "dialogue": "Bugün geldiğimiz noktada yapay zeka artık sadece bir teknoloji değil; türümüzün geleceğini şekillendiren en güçlü dönüm noktasıdır.",
                "visual": "A humanoid cybernetic being and a human standing side by side looking into an infinite cosmic dawn",
                "motion": "epic slow aerial pull back"
            }
        ]

    # Senaryo dosyasını kontrol et (parametreyle verilmişse veya dizinde senaryo.txt varsa)
    script_file = getattr(args, "script", None)
    if not script_file and os.path.exists("senaryo.txt"):
        script_file = "senaryo.txt"

    if script_file and os.path.exists(script_file):
        print(f"\n[SENARYO DOSYASI] '{script_file}' okunuyor...")
        scenes = pg.parse_script_file(script_file, mode=mode)
        print(f"  Toplam {len(scenes)} sahne başarıyla senaryodan yüklendi.")
    elif mode == "shorts":
        scenes = default_scenes
    else:
        scenes = default_scenes

    project = pg.create_project(
        project_name=name,
        title=topic,
        scenes=scenes,
        mode=mode
    )

    print("\n" + "=" * 65)
    print(f"[BASARILI] '{name}' projesi olusturuldu!")
    print(f"[PROJE KLASORU] projects/{name}/")
    print(f"[PROMPT DOSYASI] projects/{name}/google_flow_prompts.txt")
    print("=" * 65)
    print("Simdi yapmaniz gerekenler:")
    print("1. 'projects/{name}/google_flow_prompts.txt' dosyasini acin.")
    print("2. flow.google.com adresine gidip her sahnenin video promptunu ve diyalogunu girin.")
    print(f"3. Indirdiginiz sesli video kliplerini 'projects/{name}/klipler/' icine atin:")
    print("   scene_1.mp4, scene_2.mp4, scene_3.mp4...")
    print(f"4. Ardindan 'python main.py build --project {name}' komutunu calistirin.\n")


def build_project(project_name: str):
    """Google Flow'dan indirilen klipleri birleştirir, dinamik altyazı ve müzik ekler."""
    project_dir = os.path.join("projects", project_name)
    json_path = os.path.join(project_dir, "project.json")

    if not os.path.exists(json_path):
        print(f"[HATA] Proje bulunamadı: {json_path}")
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        project_data = json.load(f)

    mode = project_data.get("mode", "shorts")
    scenes = project_data.get("scenes", [])
    config = load_config()

    mode_cfg = config.get("video", {}).get("modes", {}).get(mode, {
        "width": 1080 if mode == "shorts" else 1920,
        "height": 1920 if mode == "shorts" else 1080
    })
    target_w = mode_cfg.get("width", 1080)
    target_h = mode_cfg.get("height", 1920)

    ve = VideoEngine()
    sub_engine = SubtitleEngine()

    klipler_dir = os.path.join(project_dir, "klipler")
    os.makedirs(klipler_dir, exist_ok=True)

    print(f"\n>>> '{project_name}' Projesi Derleniyor ({mode.upper()} Modu)...")

    # Klipleri kontrol et: Önce scene_X.mp4 ara, yoksa klasördeki video dosyalarını zamana göre sırala
    available_videos = sorted(
        [os.path.join(klipler_dir, f) for f in os.listdir(klipler_dir) if f.lower().endswith(('.mp4', '.mov', '.webm', '.mkv')) and not f.startswith('.')],
        key=lambda x: os.path.getmtime(x)
    )

    clip_files = []
    for idx, sc in enumerate(scenes, 1):
        expected_name = f"scene_{idx}.mp4"
        clip_path = os.path.join(klipler_dir, expected_name)
        if os.path.exists(clip_path):
            clip_files.append(clip_path)
        elif idx <= len(available_videos):
            clip_files.append(available_videos[idx - 1])
        else:
            print(f"\n[UYARI] Sahne {idx} için video klibi bulunamadı!")
            print(f"Klasörde toplam {len(available_videos)} adet video var, ama projede {len(scenes)} sahne bekleniyor.")
            return None

    # 1. Her klibin süresine göre diyalog ve altyazı zamanlamalarını hesapla
    all_word_timings = []
    current_time_offset = 0.0

    print("  Klip süreleri ve diyalog senkronizasyonu hesaplanıyor...")
    for idx, (clip_p, scene) in enumerate(zip(clip_files, scenes), 1):
        duration = ve.get_clip_duration(clip_p)
        dialogue = scene.get("dialogue", scene.get("voiceover", "")).strip()

        words = dialogue.split()
        if words:
            total_chars = max(1, sum(len(w) for w in words))
            usable_duration = max(1.0, duration - 0.4)
            clip_start = current_time_offset + 0.2
            word_time = clip_start

            for w in words:
                w_dur = (len(w) / total_chars) * usable_duration
                all_word_timings.append({
                    "text": w,
                    "start": round(word_time, 2),
                    "end": round(word_time + w_dur, 2)
                })
                word_time += w_dur

        print(f"  [Sahne {idx}] Klip: {os.path.basename(clip_p)} (Süre: {duration:.2f}s)")
        current_time_offset += duration

    # 2. Altyazı dosyasını (ASS) oluştur
    ass_path = os.path.join(project_dir, "subtitles.ass")
    sub_engine.generate_ass(all_word_timings, ass_path, mode=mode)
    print("  [OK] Dinamik stilize altyazılar hazırlandı.")

    # 3. Arka plan müziği
    music_path = os.path.join("assets", "music", "ambient_calm.mp3")
    if not os.path.exists(music_path):
        music_path = None

    # 4. Final montaj (Sadece Google Flow'un kendi orijinal sesi + Altyazı + Fon Müziği)
    os.makedirs("ciktilar", exist_ok=True)
    output_video_path = os.path.join("ciktilar", f"{project_name}_{mode}.mp4")

    print("\n  Final video işleniyor (Flow Klipleri + Orijinal Flow Sesi + Altyazı)...")
    ve.assemble_flow_clips(
        clip_paths=clip_files,
        output_video_path=output_video_path,
        target_w=target_w,
        target_h=target_h,
        background_music_path=music_path,
        narration_audio_path=None,
        subtitles_ass_path=ass_path,
        bg_music_volume=0.08,
        fps=30
    )

    print("\n" + "=" * 65)
    print(f"[TEBRIKLER] Google Flow videonuz basariyla tamamlandi!")
    print(f"Video Dosyasi : {os.path.abspath(output_video_path)}")
    print(f"Toplam Sure   : {current_time_offset:.1f} saniye")
    print("=" * 65 + "\n")
    return output_video_path


def cmd_upload(args):
    """Üretilen videoyu YouTube Data API v3 ile yükler."""
    project_name = args.project
    project_dir = os.path.join("projects", project_name)
    json_path = os.path.join(project_dir, "project.json")

    if not os.path.exists(json_path):
        print(f"[HATA] Proje bulunamadı: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        project_data = json.load(f)

    mode = project_data.get("mode", "shorts")
    video_path = os.path.join("ciktilar", f"{project_name}_{mode}.mp4")

    if not os.path.exists(video_path):
        print(f"[HATA] '{video_path}' dosyası bulunamadı! Lütfen önce 'build' komutunu çalıştırın.")
        return

    uploader = YouTubeUploader()
    privacy = args.privacy or "unlisted"
    title = project_data.get("title", "Video")
    if mode == "shorts" and "#shorts" not in title.lower():
        title = f"{title} #Shorts"

    uploader.upload_video(
        video_path=video_path,
        title=title,
        description=project_data.get("description", ""),
        tags=project_data.get("tags", []),
        privacy_status=privacy
    )


def send_telegram(message: str, title: str, event: str = "bitirdim"):
    """Telegram üzerinden bildirim gönderir (isteğe bağlı)."""
    import subprocess
    script = os.getenv("TELEGRAM_NOTIFIER_SCRIPT")
    if script and os.path.exists(script):
        try:
            subprocess.run([sys.executable, script, message, title, "--event", event], check=False)
        except Exception as e:
            print(f"[UYARI] Telegram bildirimi iletilemedi: {e}")


def cmd_flow(args):
    """Google Flow ile projenin kliplerini otomatik olarak üretir ve indirir."""
    success = start_flow_generation(args.project)
    if success:
        print(f"\n[OK] Flow indirmeleri tamamlandı! Klipleri birleştirmek için:")
        print(f"python main.py build --project {args.project}")
    return success


def cmd_auto(args):
    """Sıfırdan projeyi oluşturur, klipleri Flow ile üretir, videoyu montajlar ve opsiyonel yükler."""
    project_name = args.name or f"proje_{int(time.time())}"
    project_dir = os.path.join("projects", project_name)

    # 1. Proje yoksa oluştur
    if not os.path.exists(os.path.join(project_dir, "project.json")):
        args.name = project_name
        cmd_create(args)

    # 2. Google Flow ile klipleri otomatik üret ve indir
    print(f"\n[AŞAMA 1/3] Google Flow Otomatik Klip Üretimi Başlıyor...")
    ok = start_flow_generation(project_name)
    if not ok:
        print("[HATA] Flow klip üretimi başarısız oldu!")
        send_telegram(f"'{project_name}' projesinin klip üretimi Flow'da başarısız oldu.", "Hata Oluştu", event="hata")
        return

    # 3. Klipleri birleştir ve montajla
    print(f"\n[AŞAMA 2/3] Video Montajı ve Altyazı Giydirme...")
    final_video = build_project(project_name)
    if not final_video:
        print("[HATA] Video montajı başarısız!")
        send_telegram(f"'{project_name}' montaj işlemi başarısız oldu.", "Montaj Hatası", event="hata")
        return

    # 4. YouTube Yükleme (İsteğe bağlı)
    if getattr(args, "upload", False):
        print(f"\n[AŞAMA 3/3] YouTube'a Otomatik Yükleme...")
        args.project = project_name
        cmd_upload(args)

    # 5. Telegram Bildirimi
    send_telegram(
        f"'{project_name}' videosu Google Flow ile uçtan uca üretildi!\nDosya: {os.path.basename(final_video)}",
        "Video Otomasyonu Tamamlandı",
        event="bitirdim"
    )


def main():
    parser = argparse.ArgumentParser(description="YouTube Otomasyon Sistemi (Google Flow Modeli)")
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # create
    p_create = subparsers.add_parser("create", help="Yeni proje ve Google Flow promptları oluştur")
    p_create.add_argument("--name", type=str, help="Proje klasör adı")
    p_create.add_argument("--topic", type=str, help="Video konusu")
    p_create.add_argument("--script", type=str, help="Senaryo metin dosyası (örn: senaryo.txt)")
    p_create.add_argument("--mode", type=str, choices=["shorts", "long"], default="shorts", help="Shorts (9:16) veya Long (16:9)")

    # flow
    p_flow = subparsers.add_parser("flow", help="Google Flow üzerinden klipleri otomatik üret ve indir")
    p_flow.add_argument("--project", type=str, required=True, help="Proje adı")

    # build
    p_build = subparsers.add_parser("build", help="Klipleri birleştir ve videoyu üret")
    p_build.add_argument("--project", type=str, required=True, help="Derlenecek proje adı")

    # upload
    p_upload = subparsers.add_parser("upload", help="Videoyu YouTube'a yükle")
    p_upload.add_argument("--project", type=str, required=True, help="Yüklenecek proje adı")
    p_upload.add_argument("--privacy", type=str, choices=["public", "unlisted", "private"], default="unlisted", help="Gizlilik durumu")

    # auto (Tam Otomasyon)
    p_auto = subparsers.add_parser("auto", help="Uçtan uca tam otomasyon (Oluştur -> Flow Üret -> Montajla -> Opsiyonel Yükle)")
    p_auto.add_argument("--name", type=str, help="Proje klasör adı")
    p_auto.add_argument("--topic", type=str, help="Video konusu")
    p_auto.add_argument("--script", type=str, help="Senaryo metin dosyası (örn: senaryo.txt)")
    p_auto.add_argument("--mode", type=str, choices=["shorts", "long"], default="shorts", help="Shorts (9:16) veya Long (16:9)")
    p_auto.add_argument("--upload", action="store_true", help="Montaj sonrası otomatik YouTube'a yüklensin mi?")
    p_auto.add_argument("--privacy", type=str, choices=["public", "unlisted", "private"], default="unlisted", help="Gizlilik durumu")

    args = parser.parse_args()

    if args.command == "create":
        cmd_create(args)
    elif args.command == "flow":
        cmd_flow(args)
    elif args.command == "build":
        build_project(args.project)
    elif args.command == "upload":
        cmd_upload(args)
    elif args.command == "auto":
        cmd_auto(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
