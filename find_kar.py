import requests
import os

PARTICLES_DIR = r"C:\Users\excat\Desktop\Youtube DOSYALARI\historia\particles"
PIXABAY_KEY = "55660544-40e38f4b37085fea779630d17"

queries = [
    "snowstorm blizzard overlay black",
    "snow storm wind particles black background",
    "heavy snow wind overlay",
    "winter storm snow black background",
    "snow flakes wind blowing black"
]

for i, query in enumerate(queries):
    print(f"Trying: {query}...")
    response = requests.get(
        "https://pixabay.com/api/videos/",
        params={
            "key": PIXABAY_KEY,
            "q": query,
            "video_type": "animation",
            "per_page": 3
        }
    )
    if response.status_code == 200:
        hits = response.json().get("hits", [])
        if hits:
            video_url = hits[0]["videos"]["medium"]["url"]
            video_response = requests.get(video_url, timeout=60)
            path = os.path.join(PARTICLES_DIR, f"kar_test_{i}.mp4")
            with open(path, "wb") as f:
                f.write(video_response.content)
            print(f"  Downloaded: kar_test_{i}.mp4")

print("Done! Check particles folder and pick the best one.")
