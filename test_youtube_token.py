import os
import pickle
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "token.pickle")
CLIENT_SECRETS = os.path.join(BASE_DIR, "client_secrets.json")

print("=== YouTube Token Test ===\n")

if not os.path.exists(TOKEN_FILE):
    print("❌ token.pickle bulunamadı!")
    print("   Çözüm: Aşağıdaki komutu çalıştır:")
    print("   python generate_token.py")
    exit(1)

with open(TOKEN_FILE, "rb") as f:
    creds = pickle.load(f)

print(f"Token valid:   {creds.valid}")
print(f"Token expired: {creds.expired}")
print(f"Has refresh:   {bool(creds.refresh_token)}")
print(f"Expiry:        {creds.expiry}")
print()

if creds.expired and creds.refresh_token:
    print("⚠️  Token expire olmuş, yenileniyor...")
    creds.refresh(Request())
    with open(TOKEN_FILE, "wb") as f:
        pickle.dump(creds, f)
    print("✅ Token yenilendi ve kaydedildi!")
    print()

if not creds.valid:
    print("❌ Token geçersiz ve yenilenemedi!")
    print("   Çözüm: python generate_token.py çalıştır")
    exit(1)

print("YouTube API'ye bağlanılıyor...")
try:
    youtube = build("youtube", "v3", credentials=creds)
    response = youtube.channels().list(part="snippet", mine=True).execute()
    channel = response["items"][0]["snippet"]
    print(f"✅ Bağlantı başarılı!")
    print(f"   Kanal: {channel['title']}")
    print(f"   Kanal ID: {response['items'][0]['id']}")
    print()
    print("Token çalışıyor, GitHub Secret güncelleme için:")
    print("   Linux/Mac: base64 -w 0 token.pickle")
    print("   Windows:   certutil -encode token.pickle token_b64.txt")
except Exception as e:
    print(f"❌ API hatası: {e}")
