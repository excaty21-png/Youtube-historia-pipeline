import requests
import os
import json

PIXABAY_KEY = os.environ.get("PIXABAY_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARTICLES_DIR = os.path.join(BASE_DIR, "particles")
MUSIC_DIR = os.path.join(BASE_DIR, "music")
AMBIENT_DIR = os.path.join(BASE_DIR, "ambient")
BG_DIR = os.path.join(BASE_DIR, "backgrounds")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

os.makedirs(PARTICLES_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(AMBIENT_DIR, exist_ok=True)
os.makedirs(BG_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

# Particle mapping
PARTICLE_MAPPING = {
    "antik": "ates",
    "savas": "ates",
    "gizem": "gizem",
    "ortacag": "duman",
    "deniz": "deniz"
}

PARTICLE_QUERIES = {
    "ates": "fire particles overlay black background",
    "kar": "blizzard snow wind overlay black",
    "gizem": "gold dust particles black background",
    "duman": "light mist fog overlay black background",
    "deniz": "water droplets sparkle overlay black background"
}

def download_pixabay_video(query, output_path):
    if os.path.exists(output_path):
        print(f"  Already exists: {output_path}")
        return True
    print(f"  Downloading: {query}...")
    response = requests.get(
        "https://pixabay.com/api/videos/",
        params={"key": PIXABAY_KEY, "q": query, "video_type": "animation", "per_page": 3},
        timeout=30
    )
    if response.status_code == 200:
        hits = response.json().get("hits", [])
        if hits:
            video_url = hits[0]["videos"]["medium"]["url"]
            video_response = requests.get(video_url, timeout=60)
            with open(output_path, "wb") as f:
                f.write(video_response.content)
            print(f"  Done: {os.path.basename(output_path)}")
            return True
    print(f"  Failed: {query}")
    return False

def download_freesound_audio(query, output_path, freesound_key):
    if os.path.exists(output_path):
        print(f"  Already exists: {output_path}")
        return True
    print(f"  Downloading ambient: {query}...")
    response = requests.get(
        "https://freesound.org/apiv2/search/text/",
        params={"query": query, "filter": "duration:[60 TO 600]", "fields": "id,name,previews", "token": freesound_key},
        timeout=20
    )
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            preview_url = results[0]["previews"]["preview-hq-mp3"]
            audio = requests.get(preview_url, timeout=30)
            with open(output_path, "wb") as f:
                f.write(audio.content)
            print(f"  Done: {os.path.basename(output_path)}")
            return True
    return False

def download_font():
    font_path = os.path.join(FONTS_DIR, "Montserrat-ExtraBold.ttf")
    if os.path.exists(font_path):
        print("  Font already exists")
        return
    print("  Downloading font...")
    url = "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-ExtraBold.ttf"
    response = requests.get(url, timeout=30)
    with open(font_path, "wb") as f:
        f.write(response.content)
    print("  Font downloaded!")

def download_background():
    bg_path = os.path.join(BG_DIR, "bg1.jpg")
    if os.path.exists(bg_path):
        print("  Background already exists")
        return
    print("  Downloading background...")
    url = "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=1920&h=1080&fit=crop"
    response = requests.get(url, timeout=30)
    with open(bg_path, "wb") as f:
        f.write(response.content)
    print("  Background downloaded!")

print("=== Setting up assets ===")

print("\n1. Downloading particles...")
for name, query in PARTICLE_QUERIES.items():
    path = os.path.join(PARTICLES_DIR, f"{name}.mp4")
    download_pixabay_video(query, path)

with open(os.path.join(PARTICLES_DIR, "mapping.json"), "w") as f:
    json.dump(PARTICLE_MAPPING, f)
print("  Mapping saved!")

print("\n2. Downloading ambient sounds...")
FREESOUND_KEY = os.environ.get("FREESOUND_KEY", "adpekHL20Q8ePmZSjenQVjkEf6qFXUbxcagvRh7b")
ambient_queries = {
    "antik": "ancient wind nature ambient",
    "savas": "fire crackling ambient",
    "gizem": "dark mystery ambient wind",
    "ortacag": "fireplace crackling night",
    "deniz": "ocean waves ambient"
}
for name, query in ambient_queries.items():
    path = os.path.join(AMBIENT_DIR, f"{name}.mp3")
    download_freesound_audio(query, path, FREESOUND_KEY)

print("\n3. Downloading music...")
music_path = os.path.join(MUSIC_DIR, "ambient1.mp3")
download_freesound_audio("relaxing ambient music sleep", music_path, FREESOUND_KEY)

print("\n4. Downloading font...")
download_font()

print("\n5. Downloading background...")
download_background()

print("\n=== Setup complete! ===")
