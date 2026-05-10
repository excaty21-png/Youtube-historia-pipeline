import requests
import os

FREESOUND_KEY = "adpekHL20Q8ePmZSjenQVjkEf6qFXUbxcagvRh7b"  # freesound.org'dan ?cretsiz key al

ambient_dir = r"C:\Users\excat\Desktop\Youtube DOSYALARI\historia\ambient"
os.makedirs(ambient_dir, exist_ok=True)

# Kategoriler ve arama terimleri
categories = {
    "antik": "ancient wind nature ambient",
    "savas": "fire crackling ambient",
    "gizem": "dark mystery ambient wind",
    "ortacag": "fireplace crackling night",
    "deniz": "ocean waves ambient"
}

for category, query in categories.items():
    print(f"Searching: {query}")
    response = requests.get(
        "https://freesound.org/apiv2/search/text/",
        params={
            "query": query,
            "filter": "duration:[60 TO 600]",
            "fields": "id,name,previews",
            "token": FREESOUND_KEY
        }
    )
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            preview_url = results[0]["previews"]["preview-hq-mp3"]
            audio = requests.get(preview_url)
            path = os.path.join(ambient_dir, f"{category}.mp3")
            with open(path, "wb") as f:
                f.write(audio.content)
            print(f"  Downloaded: {category}.mp3")
    else:
        print(f"  Failed: {response.status_code}")

print("Done!")

