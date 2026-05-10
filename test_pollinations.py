import requests
import time
import os

TEMP_DIR = r"C:\Users\excat\Desktop\Youtube DOSYALARI\historia\temp"
os.makedirs(TEMP_DIR, exist_ok=True)

prompts = [
    "Ancient Mayan civilization ruins disappearing into mist, dark atmospheric, cinematic illustration",
    "Grand Mayan temples reaching sky, intricate architecture, historical cinematic, dark atmosphere",
    "Mayan city consumed by jungle vines, temples overtaken by nature, dark cinematic atmosphere",
    "Mysterious Mayan collapse mystery, drought ruins warfare, dark historical cinematic illustration",
    "Ancient mysteries await, next chapter beckoning, dark atmospheric cinematic digital art"
]

for i, prompt in enumerate(prompts):
    print(f"Generating {i+1}/{len(prompts)}: {prompt[:50]}...")
    for attempt in range(3):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1920&height=1080&nologo=true&seed={i*100}"
            response = requests.get(url, timeout=120)
            if len(response.content) > 10000:
                path = os.path.join(TEMP_DIR, f"test_seg_{i}.jpg")
                with open(path, "wb") as f:
                    f.write(response.content)
                print(f"  Saved: test_seg_{i}.jpg")
                break
            else:
                print(f"  Bad response, retrying...")
                time.sleep(3)
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(5)

print("Done! Check temp folder.")
