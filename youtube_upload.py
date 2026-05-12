import os
import pickle
import re
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import anthropic
from dotenv import load_dotenv
import requests
import json
import time
from datetime import datetime, timedelta
import pytz

load_dotenv()
_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS = os.path.join(BASE_DIR, "client_secrets.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.pickle")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

PUBLISH_HOUR = 20
PUBLISH_MINUTE = 0
SHORTS_PUBLISH_HOUR = 20
SHORTS_PUBLISH_MINUTE = 15

def get_next_publish_time():
    warsaw = pytz.timezone("Europe/Warsaw")
    now = datetime.now(warsaw)
    publish_time = now.replace(hour=PUBLISH_HOUR, minute=PUBLISH_MINUTE, second=0, microsecond=0)
    if now >= publish_time:
        publish_time += timedelta(days=1)
    return publish_time.isoformat()

def get_next_shorts_publish_time():
    warsaw = pytz.timezone("Europe/Warsaw")
    now = datetime.now(warsaw)
    publish_time = now.replace(hour=SHORTS_PUBLISH_HOUR, minute=SHORTS_PUBLISH_MINUTE, second=0, microsecond=0)
    if now >= publish_time:
        publish_time += timedelta(days=1)
    return publish_time.isoformat()

def get_youtube_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError(
                "YouTube OAuth token gecersiz ve refresh edilemiyor. "
                "Lokalde yeni token.pickle uret, base64 ile encode et ve "
                "GitHub Secrets'daki YOUTUBE_TOKEN_B64'u guncelle."
            )
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)

def generate_title_and_description(topic):
    print("   - Generating title and description...")
    response = _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"""Napisz tytul i opis YouTube dla kanalu Historia do Poduszki.
Temat: {topic}

Zwroc TYLKO JSON:
{{
  "title": "intrygujacy tytul po polsku max 70 znakow z emojis",
  "description": "opis po polsku 300-400 slow, wciagajacy, z emojis, opisuje temat historyczny, na koncu zacheta do subskrypcji Historia do Poduszki",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8"]
}}"""}]
    )
    raw = response.content[0].text.strip().replace("`json", "").replace("`", "").strip()
    try:
        data = json.loads(raw)
        return data["title"], data["description"], data["tags"]
    except json.JSONDecodeError:
        title_match = re.search(r'"title"\s*:\s*"([^"]+)"', raw)
        tags_matches = re.findall(r'"([^"]{2,30})"', raw.split('"tags"')[-1] if '"tags"' in raw else "")
        title = title_match.group(1) if title_match else topic
        description = f"Historia do Poduszki - {topic}\n\nSubskrybuj Historia do Poduszki po wiecej nocnych historii!"
        tags = tags_matches[:8] if tags_matches else ["historia", "zasypianie", "historiadopoduszki"]
        return title, description, tags

def generate_thumbnail(topic, output_path):
    from thumbnail_gen import create_thumbnail
    create_thumbnail(topic, output_path)

def upload_video(video_path, topic):
    print(f"Uploading to YouTube...")
    title, description, tags = generate_title_and_description(topic)
    print(f"   Title: {title}")
    thumbnail_path = os.path.join(TEMP_DIR, "thumbnail.jpg")
    generate_thumbnail(topic, thumbnail_path)
    youtube = get_youtube_service()

    publish_at = get_next_publish_time()
    print(f"   Scheduled for: {publish_at}")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "27",
            "defaultLanguage": "pl",
            "defaultAudioLanguage": "pl"
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at,
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   Upload progress: {int(status.progress() * 100)}%")
    video_id = response["id"]
    print(f"   Video scheduled: https://youtube.com/watch?v={video_id}")
    if os.path.exists(thumbnail_path):
        print("   - Uploading thumbnail...")
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("   - Thumbnail uploaded!")
        except Exception as e:
            print(f"   - Thumbnail error: {e}")
    return video_id

def upload_shorts(video_path, topic, main_video_id=None):
    print(f"Uploading Shorts to YouTube...")
    response = _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": f"""Napisz tytul i tagi dla YouTube Shorts.
Temat: {topic}

Zwroc TYLKO JSON:
{{
  "title": "max 60 znakow, intrygujacy, z emoji i #Shorts na koncu",
  "tags": ["shorts", "historia", "historiadopoduszki", "tag4", "tag5"]
}}"""}]
    )
    raw = response.content[0].text.strip().replace("`json", "").replace("`", "").strip()
    try:
        data = json.loads(raw)
        title = data["title"]
        tags = data["tags"]
    except json.JSONDecodeError:
        title_match = re.search(r'"title"\s*:\s*"([^"]+)"', raw)
        title = title_match.group(1) if title_match else f"{topic} #Shorts"
        tags = ["shorts", "historia", "historiadopoduszki"]

    description = "Cala historia czeka na Ciebie na kanale Historia do Poduszki!\n\nSubskrybuj i znajdz pelna wersje!\n\n#shorts #historia #historiadopoduszki #nocneopowiesci"

    shorts_publish_at = get_next_shorts_publish_time()
    print(f"   Shorts scheduled for: {shorts_publish_at}")

    youtube = get_youtube_service()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "27",
            "defaultLanguage": "pl",
            "defaultAudioLanguage": "pl"
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": shorts_publish_at,
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   Shorts upload progress: {int(status.progress() * 100)}%")
    shorts_id = response["id"]
    print(f"   Shorts scheduled: https://youtube.com/shorts/{shorts_id}")
    print(f"   Will publish at: {shorts_publish_at}")
    return shorts_id
