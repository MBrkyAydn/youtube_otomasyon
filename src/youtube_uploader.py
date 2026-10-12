"""
YouTube Data API v3 Otomatik Video Yükleyici.
Ücretsiz Google Cloud OAuth2 yetkilendirmesiyle videoları YouTube kanalına yükler.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]


class YouTubeUploader:
    def __init__(
        self,
        client_secrets_path: Optional[str] = None,
        token_path: Optional[str] = None
    ):
        self.client_secrets_path = client_secrets_path or os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "config/client_secrets.json")
        self.token_path = token_path or os.getenv("YOUTUBE_TOKEN_FILE", "config/youtube_token.json")
        self.youtube = None

    def authenticate(self) -> Any:
        """
        OAuth 2.0 kimlik doğrulamasını gerçekleştirir veya kayıtlı belirteci yeniler.
        """
        credentials = None

        if os.path.exists(self.token_path):
            try:
                credentials = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                print(f"[UYARI] Mevcut token okunamadı: {e}")

        # Eğer token yoksa veya geçersizse
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except Exception as e:
                    print(f"[BİLGİ] Token yenilenemedi, yeniden oturum açılıyor: {e}")
                    credentials = None

            if not credentials:
                if not os.path.exists(self.client_secrets_path):
                    raise FileNotFoundError(
                        f"YouTube OAuth dosyası bulunamadı: '{self.client_secrets_path}'.\n"
                        f"Lütfen Google Cloud Console'dan indirdiğiniz OAuth dosyasını bu konuma koyun.\n"
                        f"Ayrıntılı rehber için 'YOUTUBE_KURULUM.md' dosyasına bakın."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_path, SCOPES)
                print("\n[YOUTUBE AUTH] Tarayıcı açılarak Google hesabınızla oturum açmanız istenecek...")
                credentials = flow.run_local_server(port=0)

            # Yeni token'ı kaydet
            os.makedirs(os.path.dirname(os.path.abspath(self.token_path)), exist_ok=True)
            with open(self.token_path, "w", encoding="utf-8") as token_file:
                token_file.write(credentials.to_json())
            print("[OK] YouTube yetkilendirmesi başarıyla kaydedildi.")

        self.youtube = build("youtube", "v3", credentials=credentials)
        return self.youtube

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        category_id: str = "28",  # 28: Science & Technology, 27: Education
        privacy_status: str = "public",  # 'public', 'unlisted', 'private'
        made_for_kids: bool = False
    ) -> Dict[str, Any]:
        """
        Videoyu YouTube kanalına yükler.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Yüklenecek video dosyası bulunamadı: {video_path}")

        if not self.youtube:
            self.authenticate()

        body = {
            "snippet": {
                "title": title[:100],  # YouTube başlık sınırı 100 karakter
                "description": description[:5000],
                "tags": tags or ["youtube", "shorts", "yapayzeka"],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": made_for_kids
            }
        }

        print(f"\n[YOUTUBE YÜKLEME] Başlatılıyor...")
        print(f"  Başlık : {title}")
        print(f"  Gizlilik: {privacy_status}")
        print(f"  Dosya   : {video_path}")

        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            chunksize=1024 * 1024 * 8,  # 8MB chunk
            resumable=True
        )

        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                percent = int(status.progress() * 100)
                print(f"  Yükleme İlerlemesi: %{percent}...", end="\r", flush=True)

        video_id = response.get("id")
        video_url = f"https://youtu.be/{video_id}"
        print(f"\n[OK] Video başarıyla yüklendi!")
        print(f"  Video ID : {video_id}")
        print(f"  İzleme Linki: {video_url}")

        return {
            "id": video_id,
            "url": video_url,
            "title": title,
            "privacy_status": privacy_status
        }


if __name__ == "__main__":
    uploader = YouTubeUploader()
    print("YouTubeUploader modülü hazır.")
