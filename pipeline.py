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

load_dotenv()

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
BG_DIR = os.path.join(BASE_DIR, "backgrounds")
MUSIC_DIR = os.path.join(BASE_DIR, "music")
AMBIENT_DIR = os.path.join(BASE_DIR, "ambient")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

os.makedirs(TEMP_DIR, exist_ok=True)

STATE_FILE = os.path.join(BASE_DIR, "state.json")

CATEGORIES = {
    "antik": "antik.mp3",
    "savas": "savas.mp3",
    "gizem": "gizem.mp3",
    "ortacag": "ortacag.mp3",
    "deniz": "deniz.mp3"
}

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_format": "medieval_pov", "used_topics": []}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def select_topic_and_keywords(used_topics, content_format):
    client = anthropic.Anthropic(api_key=API_KEY)
    print(f"   - AI selecting topic (format: {content_format})...")
    used_str = "\n".join(f"- {t}" for t in used_topics[-50:]) if used_topics else "brak"

    if content_format == "medieval_pov":
        format_instruction = """Format: IMMERSIVE MEDIEVAL POV
Wybierz temat związany ze średniowieczem (życie codzienne, klasztory, plaga, zamki, rycerze, pielgrzymi, inkwizycja, głód, zima, wioski, lasy, modlitwa).
Temat musi być konkretną sytuacją lub momentem (nie ogólnym tematem), np:
"Noc w klasztorze podczas zarazy - 1349"
"Podróż pielgrzyma przez zimowy las - 1200"
"Ostatnia noc oblężonego zamku - 1415"
Kategoria ZAWSZE: ortacag"""
    else:
        format_instruction = """Format: HISTORICAL DOCUMENTARY
Wybierz fascynujący temat historyczny z dowolnej epoki i cywilizacji.
Może dotyczyć: starożytnych cywilizacji, wielkich odkryć, tajemnic historii, słynnych postaci, bitew, upadku imperiów, epidemii, mitów.
Dobierz odpowiednią kategorię ambient."""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=400,
        messages=[{
            "role": "user",
            "content": f"""Wybierz unikalny temat historyczny dla podcastu do zasypiania "Historia do Poduszki".

{format_instruction}

UŻYTE JUŻ TEMATY (nie powtarzaj żadnego z tych):
{used_str}

Kategorie ambient:
- antik: starożytne cywilizacje, Egipt, Grecja, Rzym, Majowie, Inkowie
- savas: wojny, bitwy, podboje, imperia
- gizem: tajemnice, zaginięcia, przepowiednie, klątwy
- ortacag: średniowiecze, krzyżowcy, dżuma, zamki
- deniz: odkrycia, Wikingowie, wyprawy morskie

Zwróć TYLKO JSON:
{{
  "topic": "unikalny temat po polsku",
  "keywords": ["english_keyword1", "english_keyword2", "english_keyword3"],
  "category": "jedna z: antik, savas, gizem, ortacag, deniz"
}}"""
        }]
    )
    raw = message.content[0].text.strip().replace("`json", "").replace("`", "").strip()
    data = json.loads(raw)
    return data["topic"], data["keywords"], data["category"]

def generate_text(topic, content_format):
    client = anthropic.Anthropic(api_key=API_KEY)
    print(f"   - Generating text ({content_format})...")

    if content_format == "medieval_pov":
        prompt = f"""Jesteś mistrzem immersyjnego storytellingu. Napisz hipnotyczny tekst po polsku w drugiej osobie ("ty", "twoje"), gdzie słuchacz przeżywa średniowiecze osobiście.

Temat: {topic}

STYL OBOWIĄZKOWY:
- Narracja w drugiej osobie: "Czujesz...", "Widzisz...", "Słyszysz...", "Twoje nogi..."
- Atmosferyczne, kinematograficzne opisy
- Detale sensoryczne: śnieg, wiatr, dzwony, świece, błoto, zamki, klasztory, konie, las, modlitwy, drewniane wioski, zimowe noce
- Krótkie, immersyjne akapity
- Powolne tempo
- Mroczny, ale spokojny ton
- Realistyczne średniowieczne życie codzienne
- Emocje: samotność, strach, przetrwanie, tajemnica, religia, głód, zaraza
- ZERO nowoczesnego języka
- Pisz jak "zapomniane wspomnienie z innego życia"
- Pauzy z ... co kilka zdań

ZASADY:
- Długość: dokładnie 1500-1700 słów
- Używaj poprawnych polskich znaków: ą, ę, ó, ś, ź, ż, ć, ń, ł
- Tylko ciągły tekst, bez nagłówków
- Ostatnie zdanie ZAWSZE: Jutro zabiorę cię w inne miejsce... Jeśli chcesz więcej, subskrybuj Historia do Poduszki..."""
    else:
        prompt = f"""Jesteś narratorem audiobooków do zasypiania o tematyce historycznej.
Napisz hipnotyczny tekst po polsku na temat: {topic}

STRUKTURA OBOWIĄZKOWA:
1. Pierwsze zdanie: bardzo intrygujące pytanie lub zaskakujące stwierdzenie (hook)
2. Powolne, spokojne rozwinięcie historii - szczegółowe opisy, atmosfera, postacie
3. Środkowa część: rozbudowane opisy historyczne, ciekawostki, detale
4. Zakończenie lekko niedopowiedziane, tajemnicze

ZASADY:
- Długość: dokładnie 1500-1700 słów
- Tempo: wolne, uspokajające zdania
- Styl: cichy, medytacyjny, jak szept przed snem
- Używaj poprawnych polskich znaków: ą, ę, ó, ś, ź, ż, ć, ń, ł
- Dodaj pauzy z ... co kilka zdań
- Tylko ciągły tekst, bez nagłówków ani podziałów
- Ostatnie zdanie ZAWSZE: Jutro opowiem ci kolejną historię... Jeśli chcesz więcej, subskrybuj Historia do Poduszki..."""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    raw_text = message.content[0].text

    if content_format == "medieval_pov":
        ending = "Jutro zabiorę cię w inne miejsce... Jeśli chcesz więcej, subskrybuj Historia do Poduszki..."
    else:
        ending = "Jutro opowiem ci kolejną historię... Jeśli chcesz więcej, subskrybuj Historia do Poduszki..."

    # Strip ending before word count check
    text_body = raw_text
    for end_variant in [ending, "Jutro opowiem", "Jutro zabiorę", "subskrybuj Historia do Poduszki"]:
        idx = text_body.rfind(end_variant[:20])
        if idx != -1:
            text_body = text_body[:idx].rstrip()
            break

    word_count = len(text_body.split())
    print(f"   - Word count: {word_count}")

    if word_count < 1500:
        needed = 1500 - word_count
        print(f"   - Too short, generating ~{needed} more words...")
        extension = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""Kontynuuj poniższy tekst historyczny w tym samym stylu i tonie.
Napisz dokładnie {needed + 100} słów - kontynuację, która płynnie łączy się z tekstem.
Nie powtarzaj tego co już jest. Nie dodawaj zakończenia ani pożegnania.
Tylko ciągły tekst, bez nagłówków.

Tekst do kontynuacji:
{text_body[-500:]}"""
            }]
        )
        text_body = text_body + "\n\n" + extension.content[0].text.strip()
        print(f"   - New word count: {len(text_body.split())}")

    raw_text = text_body + "\n\n" + ending

    print("   - Proofreading...")
    proofread = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""Jesteś native speakerem języka polskiego i redaktorem.
Popraw poniższy tekst:
1. Popraw WSZYSTKIE błędy gramatyczne i ortograficzne
2. Popraw odmianę przez przypadki
3. Upewnij się że wszystkie polskie znaki są poprawne: ą,ę,ó,ś,ź,ż,ć,ń,ł
4. Zachowaj oryginalny styl, strukturę i znaczenie
5. Zachowaj pauzy ...
6. Zachowaj ostatnie zdanie bez zmian
7. Zwróć TYLKO poprawiony tekst, zero komentarzy

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

def generate_image_prompts(text, audio_duration):
    client = anthropic.Anthropic(api_key=API_KEY)
    segment_count = max(10, int(audio_duration / 20))
    print(f"   - {int(audio_duration)}s audio → {segment_count} images needed (1 per 20s)")
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2048,
        messages=[{"role": "user", "content": f"""Podziel tekst na fragmenty po okolo 20 sekund (40-50 slow). Utworz DOKLADNIE {segment_count} segmentow.
Dla kazdego fragmentu napisz prompt do generowania obrazu AI.

Prompt musi byc:
- Po angielsku
- Styl: soft warm illustration, peaceful dreamy atmosphere, gentle golden light, historical, relaxing, pastel colors
- Maksymalnie 15 slow
- Utworz DOKLADNIE {segment_count} segmentow!

Zwroc TYLKO JSON:
{{
  "segments": [
    {{
      "text": "fragment tekstu",
      "prompt": "image prompt"
    }}
  ]
}}

Tekst:
{text}"""}]
    )
    raw = message.content[0].text.strip().replace("`json", "").replace("`", "").strip()
    try:
        data = json.loads(raw)
        return data["segments"]
    except json.JSONDecodeError:
        import re
        segments = []
        pattern = r'"text"\s*:\s*"([^"]+)"\s*,\s*"prompt"\s*:\s*"([^"]+)"'
        matches = re.findall(pattern, raw)
        for t, p in matches:
            segments.append({"text": t, "prompt": p})
        if segments:
            return segments
        raise

def download_pollinations_image(prompt, output_path, seed=0):
    import time
    for attempt in range(3):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1920&height=1080&nologo=true&seed={seed}"
            response = requests.get(url, timeout=90)
            if len(response.content) > 10000:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            time.sleep(3)
        except Exception as e:
            print(f"     Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    return False

def generate_ai_images(segments):
    import time
    print(f"   - Generating {len(segments)} AI images via Pollinations...")
    images = []
    for i, seg in enumerate(segments):
        img_path = os.path.join(TEMP_DIR, f"seg_{i}.jpg")
        print(f"     {i+1}/{len(segments)}: {seg['prompt'][:60]}...")
        success = download_pollinations_image(seg["prompt"], img_path, seed=i*100)
        if success:
            images.append(img_path)
        else:
            fallback_files = [os.path.join(BG_DIR, f) for f in os.listdir(BG_DIR) if f.endswith('.jpg')]
            if fallback_files:
                images.append(random.choice(fallback_files))
    return images

def generate_video(audio_path, images, output_path, category):
    print("   - Building video...")

    music_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith('.mp3')]
    music_path = os.path.join(MUSIC_DIR, random.choice(music_files)) if music_files else None

    ambient_file = CATEGORIES.get(category, "gizem.mp3")
    ambient_path = os.path.join(AMBIENT_DIR, ambient_file)
    has_ambient = os.path.exists(ambient_path)
    print(f"   - Category: {category} ? ambient: {ambient_file}")

    duration = get_audio_duration(audio_path)
    img_duration = 20
    fade_duration = 1

    filter_parts = []
    inputs = []

    total_frames = (img_duration + fade_duration) * 25
    for i, img_path in enumerate(images):
        inputs.extend(["-loop", "1", "-t", str(img_duration + fade_duration), "-i", img_path])
        if i % 2 == 0:
            # zoom in: 100% -> 115%
            zoom_filter = (
                f"[{i}:v]scale=8000:-1,zoompan=z='min(1+on/{total_frames}*0.15,1.15)'"
                f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={total_frames}:s=1920x1080:fps=25[v{i}]"
            )
        else:
            # zoom out: 115% -> 100%
            zoom_filter = (
                f"[{i}:v]scale=8000:-1,zoompan=z='max(1.15-on/{total_frames}*0.15,1.0)'"
                f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={total_frames}:s=1920x1080:fps=25[v{i}]"
            )
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
            f";[{len(images)}:a]volume=2.0[voice]" +
            f";[{music_idx}:a]volume=0.12[music]" +
            f";[{ambient_idx}:a]volume=0.10[ambient]" +
            f";[voice][music][ambient]amix=inputs=3:duration=first:normalize=0[audio]"
        )
        cmd.extend(["-filter_complex", full_filter, "-map", final_video_label, "-map", "[audio]"])
    elif music_path:
        full_filter = (
            filter_complex +
            f";[{len(images)}:a]volume=2.0[voice]" +
            f";[{music_idx}:a]volume=0.12[music]" +
            f";[voice][music]amix=inputs=2:duration=first:normalize=0[audio]"
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
        state = load_state()
        content_format = "documentary" if state["last_format"] == "medieval_pov" else "medieval_pov"
        print(f"FORMAT: {content_format}\n")

        print("STEP 1: AI selecting topic...")
        topic, keywords, category = select_topic_and_keywords(state["used_topics"], content_format)
        print(f"   Topic: {topic}")
        print(f"   Keywords: {keywords}")
        print(f"   Category: {category}\n")

        print("STEP 2: Generating text...")
        text = generate_text(topic, content_format)
        print(f"   Done: {len(text)} characters\n")

        audio_path = os.path.join(TEMP_DIR, f"audio_{timestamp}.mp3")
        temp_files.append(audio_path)
        print("STEP 3: Generating audio...")
        await generate_audio(text, audio_path)
        print(f"   Done\n")

        audio_duration = get_audio_duration(audio_path)
        print(f"STEP 4: Generating AI images...")
        segments = generate_image_prompts(text, audio_duration)
        images = generate_ai_images(segments)
        temp_files.extend([img for img in images if TEMP_DIR in img])
        print(f"   Done: {len(images)} images\n")

        video_path = os.path.join(OUTPUT_DIR, f"historia_{timestamp}.mp4")
        print("STEP 5: Creating video...")
        generate_video(audio_path, images, video_path, category)

        print("STEP 6: Cleaning temp files...")
        cleanup(temp_files)

        state["last_format"] = content_format
        state["used_topics"].append(topic)
        save_state(state)
        print(f"   State saved (used topics: {len(state['used_topics'])})\n")

        print(f"\n{'='*50}")
        print(f"DONE! Video ready:")
        print(f"{video_path}")
        print(f"Topic: {topic}")
        print(f"Format: {content_format}")
        print(f"{'='*50}\n")

        print("STEP 7: Uploading to YouTube...")
        try:
            from youtube_upload import upload_video
            video_id = upload_video(video_path, topic)
            print(f"   Main video uploaded: {video_id}\n")

            print("STEP 8: Creating and uploading Shorts...")
            from shorts_gen import create_shorts
            await create_shorts(topic, category, video_id, timestamp)
        except Exception as e:
            print(f"   Upload error: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"\nERROR: {e}")
        cleanup(temp_files)

asyncio.run(main())
