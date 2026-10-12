"""
YouTube OAuth Yetkilendirme Scripti.
Kullanıcı onaylı Port 8085 üzerinden çalışır.
Tarayıcıyı açar ve yetkilendirme linkini doğrudan sunar.
"""

import os
import sys
import subprocess
import wsgiref.simple_server
from google_auth_oauthlib.flow import (
    InstalledAppFlow,
    _ExclusiveWSGIServer,
    _WSGIRequestHandler,
    _RedirectWSGIApp
)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "config/client_secrets.json")
TOKEN_FILE = os.getenv("YOUTUBE_TOKEN_FILE", "config/youtube_token.json")
PORT = int(os.getenv("YOUTUBE_AUTH_PORT", "8085"))


def main():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    
    wsgi_app = _RedirectWSGIApp("Giris basarili! Bu pencereyi kapatabilirsiniz.")
    local_server = wsgiref.simple_server.make_server(
        "127.0.0.1",
        PORT,
        wsgi_app,
        server_class=_ExclusiveWSGIServer,
        handler_class=_WSGIRequestHandler
    )

    flow.redirect_uri = f"http://127.0.0.1:{PORT}/"
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    # URL'yi dosyaya yaz
    with open("AUTH_URL.txt", "w", encoding="utf-8") as f:
        f.write(auth_url)
        f.flush()

    print(f"\n[URL_HAZIR] Port: {PORT}", flush=True)

    # Windows'ta Chrome'u doğrudan aç
    try:
        subprocess.run(["powershell.exe", "-Command", f'Start-Process "{auth_url}"'], check=False)
    except Exception as e:
        print(f"Tarayici acilamadi: {e}", flush=True)

    try:
        print("[BEKLIYOR] Tarayicida onay vermeniz bekleniyor...", flush=True)
        local_server.handle_request()

        auth_response = wsgi_app.last_request_uri.replace("http", "https")
        flow.fetch_token(authorization_response=auth_response)

        os.makedirs(os.path.dirname(os.path.abspath(TOKEN_FILE)), exist_ok=True)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(flow.credentials.to_json())

        print("\n[SUCCESS] YouTube hesabi basariyla baglandi!", flush=True)
    finally:
        local_server.server_close()


if __name__ == "__main__":
    main()
