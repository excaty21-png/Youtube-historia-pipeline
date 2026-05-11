import asyncio
import edge_tts
import anthropic
import subprocess
import os
import random
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(r"C:\Users\excat\Desktop\historia\.env")

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
BASE_DIR = r"C:\Users\excat\Desktop\historia"
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
BG_DIR = os.path.join(BASE_DIR, "backgrounds")
MUSIC_DIR = os.path.join(BASE_DIR, "music")
AMBIENT_DIR = os.path.join(BASE_DIR, "ambient")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

os.makedirs(TEMP_DIR, exist_ok=True)

HISTORIA_TOPICS = [
    "Zagini?cie Maj?w - koniec wielkiej cywilizacji",
    "Aleksander Wielki - podb?j ?wiata w 10 lat",
    "Czarna ?mier? - d?uma kt?ra zmieni?a Europ?",
    "Kleopatra - ostatnia faraonka Egiptu",
    "Wikingowie w Ameryce - przed Kolumbem",
    "Pompeje - miasto zamro?one w czasie",
    "Biblioteka Aleksandryjska - utracona wiedza ?wiata",
    "Czyngis-chan - najwi?ksze imperium w historii",
    "Atlantyda - mit czy rzeczywisto??",
    "Krzy?owcy - w imi? Boga i z?ota",
    "Inkowie - imperium bez ko?a i pisma",
    "Rasputin - cz?owiek kt?rego nie mo?na by?o zabi?",
    "Tutanchamon - kl?twa faraona",
    "Spartanie - wojownicy kt?rzy bali si? tylko jednego",
    "Nostradamus - proroctwa kt?re si? spe?ni?y"
]

CATEGORIES = {
    "antik": "antik.mp3",
    "savas": "savas.mp3",
    "gizem": "gizem.mp3",
    "ortacag": "ortacag.mp3",
    "deniz": "deniz.mp3"
}

def select_topic_and_keywords():
    client = anthropic.Anthropic(api_key=API_KEY)
    print("   - AI selecting topic, keywords and category...")
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""Wybierz jeden temat z tej listy i wygeneruj s?owa kluczowe oraz kategori?.

Lista temat?w:
{chr(10).join(HISTORIA_TOPICS)}

Kategorie ambient:
- antik: staro?ytne cywilizacje, Egipt, Grecja, Rzym, Majowie, Inkowie
- savas: wojny, bitwy, podboje, imperia, Aleksander, Czyngis-chan
- gizem: tajemnice, zagini?cia, przepowiednie, Atlantyda, kl?twy
- ortacag: ?redniowiecze, krzy?owcy, d?uma, zamki
- deniz: odkrycia, Wikingowie, wyprawy morskie

Zwr?? TYLKO JSON, zero komentarzy:
{{
  "topic": "wybrany temat",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "category": "jedna z: antik, savas, gizem, ortacag, deniz"
}}

S?owa kluczowe po angielsku, historyczne zdj?cia pasuj?ce do tematu."""
        }]
    )
    raw = message.content[0].text.strip().replace("`json", "").replace("`", "").strip()
    data = json.loads(raw)
    return data["topic"], data["keywords"], data["category"]

def generate_text(topic):
    client = anthropic.Anthropic(api_key=API_KEY)
    print("   - Generating text with Haiku...")
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=700,
        messages=[{
            "role": "user",
            "content": f"""Jeste? narratorem audiobook?w do zasypiania o tematyce historycznej.
Napisz hipnotyczny tekst po polsku na temat: {topic}

STRUKTURA OBOWI?ZKOWA:
1. Pierwsze zdanie: bardzo intryguj?ce pytanie lub zaskakuj?ce stwierdzenie (hook)
2. Powolne, spokojne rozwini?cie historii
3. Zako?czenie lekko niedopowiedziane, tajemnicze

ZASADY:
- D?ugo??: dok?adnie 200-220 s??w
- Tempo: wolne, uspokajaj?ce zdania
- Styl: cichy, medytacyjny, jak szept przed snem
- U?ywaj poprawnych polskich znak?w: ?, ?, ?, ?, ?, ?, ?, ?, ?
- Dodaj pauzy z ... co kilka zda?
- Tylko ci?g?y tekst, bez nag??wk?w
- Ostatnie zdanie ZAWSZE: Jutro opowiem ci kolejn? histori?... Je?li chcesz wi?cej, subskrybuj Historia do Poduszki..."""
        }]
    )
    raw_text = message.content[0].text
    print("   - Proofreading with Sonnet...")
    proofread = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=700,
        messages=[{
            "role": "user",
            "content": f"""Jeste? native speakerem j?zyka polskiego i redaktorem.
Popraw poni?szy tekst:
1. Popraw WSZYSTKIE b??dy gramatyczne i ortograficzne
2. Popraw odmian? przez przypadki
3. Upewnij si? ?e wszystkie polskie znaki s? poprawne: ?,?,?,?,?,?,?,?,?
4. Zachowaj oryginalny styl, struktur? i znaczenie
5. Zachowaj pauzy ...
6. Zachowaj ostatnie zdanie: Jutro opowiem ci kolejn? histori?... Je?li chcesz wi?cej, subskrybuj Historia do Poduszki...
7. Zwr?? TYLKO poprawiony tekst, zero komentarzy

Tekst:
{raw_text}"""
        }]
    )
    return proofread.content[0].text

async def generate_audio(text, output_path):
    communicate = edge_tts.Communicate(text, "pl-PL-MarekNeural", rate="-10%")
    await communicate.save(output_path)
    print(f"   - Audio saved")

def get_audio_duration(audio_path):
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", audio_path
    ], capture_output=True, text=True)
    if not result.stdout.strip():
        raise RuntimeError(f"ffprobe returned no output for {audio_path}. stderr: {result.stderr.strip()}")
    data = json.loads(result.stdout)
    if "format" not in data:
        raise RuntimeError(f"ffprobe output missing 'format' key: {data}")
    return float(data["format"]["duration"])

def download_images(keywords, count):
    print(f"   - Downloading {count} images from Unsplash...")
    images = []
    keyword_cycle = keywords * 10
    for i, keyword in enumerate(keyword_cycle):
        if len(images) >= count:
            break
        try:
            response = requests.get(
                "https://api.unsplash.com/photos/random",
                params={"query": keyword, "orientation": "landscape", "client_id": UNSPLASH_KEY},
                timeout=10
            )
            if response.status_code == 200:
                img_url = response.json()["urls"]["regular"]
                img_response = requests.get(img_url, timeout=15)
                img_path = os.path.join(TEMP_DIR, f"img_{i}.jpg")
                with open(img_path, "wb") as f:
                    f.write(img_response.content)
                images.append(img_path)
                print(f"     {len(images)}/{count}: {keyword}")
        except Exception as e:
            print(f"     Failed: {e}")
    while len(images) < count:
        fallback_files = [os.path.join(BG_DIR, f) for f in os.listdir(BG_DIR) if f.endswith('.jpg')]
        if fallback_files:
            images.append(random.choice(fallback_files))
        else:
            break
    return images[:count]

def generate_video(audio_path, images, output_path, category):
    print("   - Building video...")

    music_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith('.mp3')]
    music_path = os.path.join(MUSIC_DIR, random.choice(music_files)) if music_files else None

    ambient_file = CATEGORIES.get(category, "gizem.mp3")
    ambient_path = os.path.join(AMBIENT_DIR, ambient_file)
    has_ambient = os.path.exists(ambient_path)
    print(f"   - Category: {category} ? ambient: {ambient_file}")

    duration = get_audio_duration(audio_path)
    img_duration = 30
    fade_duration = 1

    filter_parts = []
    inputs = []

    for i, img_path in enumerate(images):
        inputs.extend(["-loop", "1", "-t", str(img_duration + fade_duration), "-i", img_path])
        if i % 2 == 0:
            zoom_filter = f"[{i}:v]scale=1920:-1,zoompan=z='min(zoom+0.0008,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={(img_duration+fade_duration)*25}:s=1920x1080:fps=25[v{i}]"
        else:
            zoom_filter = f"[{i}:v]scale=1920:-1,zoompan=z='if(lte(zoom,1.0),1.3,max(1.0,zoom-0.0008))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={(img_duration+fade_duration)*25}:s=1920x1080:fps=25[v{i}]"
        filter_parts.append(zoom_filter)

    filter_complex = ";".join(filter_parts)
    if len(images) > 1:
        prev = "[v0]"
        for i in range(1, len(images)):
            offset = i * img_duration - fade_duration * i
            label = f"[xf{i}]"
            filter_complex += f";{prev}[v{i}]xfade=transition=fade:duration={fade_duration}:offset={offset}{label}"
            prev = label
        final_video_label = f"[xf{len(images)-1}]"
    else:
        final_video_label = "[v0]"

    cmd = ["ffmpeg", "-y"]
    cmd.extend(inputs)
    cmd.extend(["-i", audio_path])

    audio_inputs_count = len(images) + 1

    if music_path:
        cmd.extend(["-i", music_path])
        music_idx = audio_inputs_count
        audio_inputs_count += 1

    if has_ambient:
        cmd.extend(["-i", ambient_path])
        ambient_idx = audio_inputs_count

    if music_path and has_ambient:
        full_filter = (
            filter_complex +
            f";[{len(images)}:a]volume=1.0[voice]" +
            f";[{music_idx}:a]volume=0.10[music]" +
            f";[{ambient_idx}:a]volume=0.08[ambient]" +
            f";[voice][music][ambient]amix=inputs=3:duration=first[audio]"
        )
        cmd.extend(["-filter_complex", full_filter, "-map", final_video_label, "-map", "[audio]"])
    elif music_path:
        full_filter = (
            filter_complex +
            f";[{len(images)}:a]volume=1.0[voice]" +
            f";[{music_idx}:a]volume=0.12[music]" +
            f";[voice][music]amix=inputs=2:duration=first[audio]"
        )
        cmd.extend(["-filter_complex", full_filter, "-map", final_video_label, "-map", "[audio]"])
    else:
        cmd.extend(["-filter_complex", filter_complex, "-map", final_video_label, "-map", f"{len(images)}:a"])

    cmd.extend(["-c:v", "libx264", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", "-t", str(duration), "-pix_fmt", "yuv420p", output_path])

    try:
        subprocess.run(cmd, check=True)
        print(f"   - Video saved: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"   - FFmpeg error: {e}")
        raise

def cleanup(paths):
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except:
            pass
    print("   - Temp files cleaned")

async def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_files = []

    print(f"\n{'='*50}")
    print(f"HISTORIA DO PODUSZKI - PIPELINE")
    print(f"{'='*50}\n")

    try:
        print("STEP 1: AI selecting topic...")
        topic, keywords, category = select_topic_and_keywords()
        print(f"   Topic: {topic}")
        print(f"   Keywords: {keywords}")
        print(f"   Category: {category}\n")

        print("STEP 2: Generating text...")
        text = generate_text(topic)
        print(f"   Done: {len(text)} characters\n")

        audio_path = os.path.join(TEMP_DIR, f"audio_{timestamp}.mp3")
        temp_files.append(audio_path)
        print("STEP 3: Generating audio...")
        await generate_audio(text, audio_path)
        print(f"   Done\n")

        audio_duration = get_audio_duration(audio_path)
        photo_count = max(3, int(audio_duration / 30) + 1)
        print(f"STEP 4: Downloading images...")
        print(f"   Video: {int(audio_duration)}s, 30s/photo = {photo_count} photos needed")
        images = download_images(keywords, count=photo_count)
        temp_files.extend([img for img in images if TEMP_DIR in img])
        print(f"   Done: {len(images)} images\n")

        video_path = os.path.join(OUTPUT_DIR, f"historia_{timestamp}.mp4")
        print("STEP 5: Creating video...")
        generate_video(audio_path, images, video_path, category)

        print("STEP 6: Cleaning temp files...")
        cleanup(temp_files)

        print(f"\n{'='*50}")
        print(f"DONE! Video ready:")
        print(f"{video_path}")
        print(f"Topic: {topic}")
        print(f"{'='*50}\n")

    except Exception as e:
        print(f"\nERROR: {e}")
        cleanup(temp_files)

asyncio.run(main())
