import os
import sys
import pickle
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "token.pickle")

def get_youtube():
    with open(TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)

def find_latest_video():
    output_dir = os.path.join(BASE_DIR, "output")
    videos = [f for f in os.listdir(output_dir) if f.endswith(".mp4") and f.startswith("historia_")]
    if not videos:
        return None
    videos.sort(reverse=True)
    return os.path.join(output_dir, videos[0])

video_path = find_latest_video()
if not video_path:
    print("HATA: output/ klasorunde video bulunamadi!")
    sys.exit(1)

print(f"Video bulundu: {os.path.basename(video_path)}")
print(f"Boyut: {os.path.getsize(video_path) / 1024 / 1024:.1f} MB")
print()
print("YouTube'a yukleniyor (PRIVATE, hemen silebilirsin)...")

youtube = get_youtube()

body = {
    "snippet": {
        "title": "TEST - Historia do Poduszki - silebilirsin",
        "description": "Bu bir test yuklemesidir.",
        "categoryId": "27",
        "defaultLanguage": "pl",
    },
    "status": {
        "privacyStatus": "private",
        "selfDeclaredMadeForKids": False
    }
}

media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"  %{int(status.progress() * 100)} yuklendi...")

video_id = response["id"]
print()
print(f"BASARILI! https://youtube.com/watch?v={video_id}")
print("YouTube Studio'dan silebilirsin.")
