import requests
import os

PARTICLES_DIR = r"C:\Users\excat\Desktop\Youtube DOSYALARI\historia\particles"
PIXABAY_KEY = "55660544-40e38f4b37085fea779630d17"

print("Searching windy snow...")
response = requests.get(
    "https://pixabay.com/api/videos/",
    params={
        "key": PIXABAY_KEY,
        "q": "blizzard snow wind overlay black background",
        "video_type": "animation",
        "per_page": 5
    }
)
if response.status_code == 200:
    hits = response.json().get("hits", [])
    if hits:
        video_url = hits[0]["videos"]["medium"]["url"]
        video_response = requests.get(video_url, timeout=60)
        path = os.path.join(PARTICLES_DIR, "kar.mp4")
        with open(path, "wb") as f:
            f.write(video_response.content)
        print("Downloaded: kar.mp4")
    else:
        print("No results!")
else:
    print(f"Failed: {response.status_code}")
