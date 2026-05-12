import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "token.pickle")
CLIENT_SECRETS = os.path.join(BASE_DIR, "client_secrets.json")

if not os.path.exists(CLIENT_SECRETS):
    print("❌ client_secrets.json bulunamadı!")
    print("   Google Cloud Console > APIs > YouTube Data API v3 > Credentials")
    print("   OAuth 2.0 Client ID oluştur (Desktop app), JSON indir, client_secrets.json olarak kaydet")
    exit(1)

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
creds = flow.run_local_server(port=0)

with open(TOKEN_FILE, "wb") as f:
    pickle.dump(creds, f)

print(f"✅ token.pickle oluşturuldu!")
print()
print("GitHub Secret güncelleme için:")
print("   Windows: certutil -encode token.pickle token_b64.txt")
print("   Sonra token_b64.txt içeriğini YOUTUBE_TOKEN_B64 secret'ına kopyala")
print()
print("   Linux/Mac: base64 -w 0 token.pickle | pbcopy")
