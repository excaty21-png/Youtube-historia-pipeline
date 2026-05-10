import requests
import os

output_dir = r"C:\Users\excat\Desktop\Youtube DOSYALARI\historia\backgrounds"

images = [
    ("https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=1920&h=1080&fit=crop", "bg1.jpg"),
    ("https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1920&h=1080&fit=crop", "bg2.jpg"),
    ("https://images.unsplash.com/photo-1553913861-c0fddf2619ee?w=1920&h=1080&fit=crop", "bg3.jpg"),
    ("https://images.unsplash.com/photo-1604076913837-52ab5629fba9?w=1920&h=1080&fit=crop", "bg4.jpg"),
    ("https://images.unsplash.com/photo-1571406252241-db0280bd36cd?w=1920&h=1080&fit=crop", "bg5.jpg"),
]

for url, filename in images:
    path = os.path.join(output_dir, filename)
    response = requests.get(url)
    with open(path, "wb") as f:
        f.write(response.content)
    print(f"Downloaded: {filename}")

print("All backgrounds downloaded!")
