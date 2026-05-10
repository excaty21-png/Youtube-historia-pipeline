import requests
import os

PARTICLES_DIR = r"C:\Users\excat\Desktop\Youtube DOSYALARI\historia\particles"
PIXABAY_KEY = "55660544-40e38f4b37085fea779630d17"

particles = {
    "gizem": "gold dust particles black background",
    "duman": "light mist fog overlay black background",
    "deniz": "water droplets sparkle overlay black background"
}

for name, query in particles.items():
    print(f"Searching: {query}...")
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
            path = os.path.join(PARTICLES_DIR, f"{name}.mp4")
            with open(path, "wb") as f:
                f.write(video_response.content)
            print(f"  Downloaded: {name}.mp4")
        else:
            print(f"  No results for: {query}")
    else:
        print(f"  Failed: {response.status_code}")

print("Done!")
