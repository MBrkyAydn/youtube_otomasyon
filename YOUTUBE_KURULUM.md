# YouTube Otomatik Yükleme Kurulum Rehberi (0 TL - Ücretsiz)

YouTube Data API v3 Google'ın resmi ücretsiz servisidir. Günlük yaklaşık 6 videoyu 0 TL'ye otomatik yükleyebilirsiniz.

---

### Adım 1: Google Cloud Projesi Oluşturma
1. [Google Cloud Console](https://console.cloud.google.com/) sayfasına gidin ve YouTube kanalınızın olduğu Google hesabıyla giriş yapın.
2. Üst menüden **"Select a project" -> "New Project" (Yeni Proje)** deyin.
3. Proje adına `Youtube-Otomasyon` yazıp **Create** butonuna tıklayın.

### Adım 2: YouTube Data API v3'ü Etkinleştirme
1. Sol menüden **"APIs & Services" -> "Library" (Kütüphane)** seçeneğine gidin.
2. Arama kutusuna `YouTube Data API v3` yazın.
3. Çıkan sonuca tıklayıp **"Enable" (Etkinleştir)** butonuna basın.

### Adım 3: OAuth İstemci Dosyasını İndirme
1. Sol menüden **"APIs & Services" -> "OAuth consent screen" (OAuth İzin Ekranı)** bölümüne gidin:
   - User Type: **External** seçin ve *Create* deyin.
   - App name: `Youtube Otomasyon` yazın, e-posta adresinizi seçin ve kaydedin.
2. Sol menüden **"Credentials" (Kimlik Bilgileri)** sekmesine geçin:
   - Üstten **"+ CREATE CREDENTIALS" -> "OAuth client ID"** seçin.
   - Application type: **Desktop app (Masaüstü uygulaması)** seçin.
   - Name: `Youtube Uploader` yazıp **Create** deyin.
3. Açılan pencerede **"DOWNLOAD JSON"** butonuna tıklayarak dosyayı indirin.
4. İndirdiğiniz bu JSON dosyasının adını `client_secrets.json` olarak değiştirip şu konuma yapıştırın:
   `config/client_secrets.json` (veya `.env` dosyasında belirttiğiniz yol)

---

### Adım 4: İlk Yükleme ve Yetkilendirme
Kurulum tamamlandı! Artık tek yapmanız gereken:

```bash
python main.py upload --project test_shorts --privacy unlisted
```

İlk çalıştırmada tarayıcınızda bir Google oturum açma sayfası açılacaktır. Kanalınızı seçip *"İzin Ver"* dediğinizde oturum anahtarı kaydedilir. Sonraki hiçbir yüklemede tekrar sormaz, videoları tek komutla yükler.
