# YouTube Otomasyon Sistemi

Bu proje; YouTube Shorts (9:16) ve Yatay Uzun Videolar (16:9) için senaryodan videoya, altyazıdan seslendirmeye ve YouTube yüklemesine kadar tüm süreci sıfır API maliyetiyle otomatikleştiren yerel bir üretim motorudur.

---

## 🚀 Temel Özellikler

- **Sıfır Maliyet (0 TL) & API Key Derdi Yok:** 
  - Seslendirme: Yerel yüksek kaliteli Türkçe TTS motoru (`gTTS` ve `edge-tts`).
  - Video Kurgu & Montaj: FFmpeg ile sinematik Ken Burns (zoom-in / zoom-out) ve geçiş efektleri.
  - Altyazı: Dinamik, yüksek görünürlüklü, renklendirilmiş ASS altyazılar (Shorts'ta ortalı & büyük, Uzun videoda alt bant).
  - Fon Müziği: Telifsiz hafif ambiyans arka plan müziği (otomatik ses kısma / audio ducking ile).
- **Google Flow (flow.google.com) Entegrasyonu:**
  - Günlük 1050 kredinizi en verimli şekilde kullanmanız için her sahneye özel hazır promptlar üretir.
  - Tek tıkla kopyalayıp Flow'a yapıştırabilir, indirilen görselleri projeye atabilirsiniz.
- **YouTube Otomatik Yükleme (Ücretsiz):**
  - YouTube Data API v3 ile günlük 6 videoya kadar tamamen ücretsiz otomatik yükleme (başlık, açıklama, etiketler).
- **Çift Format Desteği:**
  - `--mode shorts`: 1080x1920 dikey Shorts formatı.
  - `--mode long`: 1920x1080 Full HD yatay video formatı (10+ dakikalık videolara tam uyumlu).

---

## 📁 Dizin Yapısı

```
Youtube_otomasyon/
│
├── config/
│   ├── config.json              # Ses, çözünürlük, müzik seviyesi ayarları
│   └── prompt_skeleton.json     # Google Flow prompt iskeleti ve stilleri
│
├── src/
│   ├── tts_engine.py            # Seslendirme motoru
│   ├── video_engine.py          # FFmpeg Ken Burns & kurgu motoru
│   ├── subtitle_engine.py       # Dinamik ASS/SRT altyazı motoru
│   ├── prompt_generator.py      # Sahne ve prompt üretici
│   ├── test_visuals.py          # Görsel eksikse sinematik kart üretici
│   └── youtube_uploader.py      # YouTube Data API v3 yükleyici
│
├── assets/
│   └── music/                   # Arka plan müzikleri (ambient_calm.mp3)
│
├── projects/                    # Oluşturulan projeler ve sahne promptları
│   └── <proje_adi>/
│       ├── google_flow_prompts.txt  # Flow'a yapıştırılacak hazır promptlar
│       ├── project.json             # Sahne ve metin verileri
│       └── gorseller/               # scene_1.png, scene_2.png...
│
├── ciktilar/                    # Nihai üretilen .mp4 video dosyaları
├── main.py                      # Ana komut satırı arayüzü (CLI)
├── requirements.txt
└── README.md
```

---

## 🛠️ Kullanım Rehberi (Adım Adım)

### 1. Yeni Proje Oluşturma
Herhangi bir konu için yeni bir proje ve Google Flow promptları oluşturmak için:

```bash
# Shorts için:
python main.py create --name felsefe_1 --topic "Stoacılık ve Zihin Kontrolü" --mode shorts

# Uzun video için:
python main.py create --name tarih_belgesel --topic "Yapay Zekanın Doğuşu" --mode long
```

Bu komut çalışınca:
- `projects/<proje_adi>/google_flow_prompts.txt` dosyası oluşur.

### 2. Google Flow'dan Görselleri Alma
1. `projects/<proje_adi>/google_flow_prompts.txt` dosyasını açın.
2. Sahne 1, Sahne 2... promptlarını sırayla kopyalayıp [flow.google.com](https://flow.google.com) adresine yapıştırın.
3. İndirdiğiniz görselleri `projects/<proje_adi>/gorseller/` içine `scene_1.png`, `scene_2.png`, `scene_3.png` olarak kaydedin.

### 3. Videoyu Render Alma (Kurgu & Montaj)
Görseller klasöre atıldıktan sonra tek bir komutla video üretilir:

```bash
python main.py build --project felsefe_1
```

Bu komut:
- Metinleri seslendirir,
- Dinamik altyazıları oluşturur,
- Görsellere sinematik kamera hareketleri (Ken Burns) ekler,
- Arka plan müziğini bağlar,
- Ve `ciktilar/<proje_adi>_shorts.mp4` dosyası olarak videoyu teslim eder!

### 4. YouTube'a Yükleme (İsteğe Bağlı)
Videoyu otomatik olarak YouTube kanalınıza yüklemek için:

```bash
# Liste dışı (önce kontrol etmek için):
python main.py upload --project felsefe_1 --privacy unlisted

# Doğrudan herkese açık yayınlamak için:
python main.py upload --project felsefe_1 --privacy public
```

---

## ⚙️ Prompt İskeletini Özelleştirme
Prompt şablonunu dilediğiniz zaman `config/prompt_skeleton.json` dosyasından değiştirebilirsiniz. Kendi özel tarzınızı veya karakter detaylarınızı buraya ekleyebilirsiniz.
