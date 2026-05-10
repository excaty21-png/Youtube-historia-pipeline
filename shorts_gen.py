import asyncio
import edge_tts
import google.generativeai as genai
import subprocess
import os
import random
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
_model = genai.GenerativeModel("gemini-2.5-pro")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
MUSIC_DIR = os.path.join(BASE_DIR, "music")
AMBIENT_DIR = os.path.join(BASE_DIR, "ambient")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
BG_DIR = os.path.join(BASE_DIR, "backgrounds")
PARTICLES_DIR = os.path.join(BASE_DIR, "particles")

CATEGORIES = {
    "antik": {"ambient": "antik.mp3", "particle": "ates"},
    "savas": {"ambient": "savas.mp3", "particle": "ates"},
    "gizem": {"ambient": "gizem.mp3", "particle": "gizem"},
    "ortacag": {"ambient": "ortacag.mp3", "particle": "duman"},
    "deniz": {"ambient": "deniz.mp3", "particle": "deniz"}
}

def generate_shorts_text(topic):
    print("   - Generating Shorts text...")

    clean_topic = topic.replace("IMMERSIVE: ", "").replace("PODRÓŻ: ", "").replace("BELGESEL: ", "")

    response = _model.generate_content(f"""Napisz krotki tekst po polsku dla YouTube Shorts na temat: {clean_topic}

Tekst musi byc gotowy do czytania przez lektora - TYLKO sam tekst, zero tytulow, zero nagłówków, zero komentarzy.

Zacznij od bardzo mocnego, zaskakujacego zdania.
Nastepnie 3-4 zdania budujace ciekawosc i napiecie.
Zakoncz slowami: Cała historia czeka na Ciebie na kanale Historia do Poduszki...

Dlugosc: 80-90 slow. Styl: dynamiczny, tajemniczy. Pauzy z ... w kluczowych momentach. Nie koncz historii.

Zwroc TYLKO gotowy tekst do czytania, nic wiecej.""")
    return response.text

def generate_shorts_image_prompts(text):
    response = _model.generate_content(f"""Podziel tekst na fragmenty po okolo 10 sekund (15-20 slow).
Dla kazdego fragmentu napisz prompt do generowania obrazu AI w formacie pionowym.

Prompt musi byc:
- Po angielsku
- Styl: soft warm illustration, peaceful dreamy atmosphere, gentle golden light, historical, vertical composition
- Maksymalnie 12 slow

Zwroc TYLKO JSON:
{{
  "segments": [
    {{
      "text": "fragment",
      "prompt": "vertical image prompt"
    }}
  ]
}}

Tekst:
{text}""")
    raw = response.text.strip().replace("`json", "").replace("`", "").strip()
    try:
        data = json.loads(raw)
        return data["segments"]
    except json.JSONDecodeError:
        import re
        segments = []
        pattern = r'"text"\s*:\s*"([^"]+)"\s*,\s*"prompt"\s*:\s*"([^"]+)"'
        matches = re.findall(pattern, raw)
        for text, prompt in matches:
            segments.append({"text": text, "prompt": prompt})
        if segments:
            return segments
        raise

def download_image(prompt, output_path, seed=0):
    for attempt in range(3):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1080&height=1920&nologo=true&seed={seed}"
            response = requests.get(url, timeout=120)
            if len(response.content) > 10000:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            time.sleep(3)
        except Exception as e:
            print(f"     Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    return False

async def generate_audio(text, output_path):
    communicate = edge_tts.Communicate(text, "pl-PL-MarekNeural", rate="-5%")
    await communicate.save(output_path)

def get_audio_duration(audio_path):
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", audio_path
    ], capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])

def get_particle_path(category):
    mapping_file = os.path.join(PARTICLES_DIR, "mapping.json")
    if not os.path.exists(mapping_file):
        return None
    with open(mapping_file) as f:
        mapping = json.load(f)
    particle_name = mapping.get(category, "gizem")
    particle_path = os.path.join(PARTICLES_DIR, f"{particle_name}.mp4")
    return particle_path if os.path.exists(particle_path) else None

def generate_shorts_video(audio_path, images, output_path, category="gizem"):
    print("   - Building Shorts video...")

    music_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith('.mp3')]
    music_path = os.path.join(MUSIC_DIR, random.choice(music_files)) if music_files else None

    cat_data = CATEGORIES.get(category, CATEGORIES["gizem"])
    ambient_path = os.path.join(AMBIENT_DIR, cat_data["ambient"])
    has_ambient = os.path.exists(ambient_path)

    particle_path = get_particle_path(category)
    has_particles = particle_path is not None

    duration = get_audio_duration(audio_path)
    img_duration = 10
    fade_duration = 1

    filter_parts = []
    inputs = []

    for i, img_path in enumerate(images):
        inputs.extend(["-loop", "1", "-t", str(img_duration + fade_duration), "-i", img_path])
        if i % 2 == 0:
            zoom_filter = f"[{i}:v]scale=2160:-1,zoompan=z='min(zoom+0.0003,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={(img_duration+fade_duration)*25}:s=1080x1920:fps=25[v{i}]"
        else:
            zoom_filter = f"[{i}:v]scale=2160:-1,zoompan=z='if(lte(zoom,1.0),1.3,max(1.0,zoom-0.0003))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={(img_duration+fade_duration)*25}:s=1080x1920:fps=25[v{i}]"
        filter_parts.append(zoom_filter)

    filter_complex = ";".join(filter_parts)
    if len(images) > 1:
        prev = "[v0]"
        for i in range(1, len(images)):
            offset = i * img_duration - fade_duration * i
            label = f"[xf{i}]"
            filter_complex += f";{prev}[v{i}]xfade=transition=fade:duration={fade_duration}:offset={offset}{label}"
            prev = label
        base_video_label = f"[xf{len(images)-1}]"
    else:
        base_video_label = "[v0]"

    next_input_idx = len(images)
    cmd = ["ffmpeg", "-y"]
    cmd.extend(inputs)
    cmd.extend(["-i", audio_path])
    next_input_idx += 1

    music_idx = None
    ambient_idx = None
    particle_idx = None

    if music_path:
        cmd.extend(["-i", music_path])
        music_idx = next_input_idx
        next_input_idx += 1

    if has_ambient:
        cmd.extend(["-i", ambient_path])
        ambient_idx = next_input_idx
        next_input_idx += 1

    if has_particles:
        cmd.extend(["-stream_loop", "-1", "-i", particle_path])
        particle_idx = next_input_idx
        next_input_idx += 1

    if has_particles:
        base_label_clean = base_video_label.strip("[]")
        final_filter = filter_complex + f";[{particle_idx}:v]scale=1080:1920,fps=25[pscaled];[{base_label_clean}][pscaled]blend=all_mode=screen:all_opacity=0.4[finalvideo]"
        final_video_label = "[finalvideo]"
    else:
        final_video_label = base_video_label

    audio_idx = len(images)
    if music_path and has_ambient:
        audio_filter = (
            f";[{audio_idx}:a]volume=1.0[voice]"
            f";[{music_idx}:a]volume=0.10[music]"
            f";[{ambient_idx}:a]volume=0.08[ambient]"
            f";[voice][music][ambient]amix=inputs=3:duration=first[audio]"
        )
    elif music_path:
        audio_filter = (
            f";[{audio_idx}:a]volume=1.0[voice]"
            f";[{music_idx}:a]volume=0.12[music]"
            f";[voice][music]amix=inputs=2:duration=first[audio]"
        )
    else:
        audio_filter = ""

    full_filter = final_filter + audio_filter if audio_filter else final_filter

    if audio_filter:
        cmd.extend(["-filter_complex", full_filter, "-map", final_video_label, "-map", "[audio]"])
    else:
        cmd.extend(["-filter_complex", full_filter, "-map", final_video_label, "-map", f"{audio_idx}:a"])

    cmd.extend([
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        output_path
    ])

    try:
        subprocess.run(cmd, check=True)
        print(f"   - Shorts video saved: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"   - FFmpeg error: {e}")
        raise

async def create_shorts(topic, category, main_video_id, timestamp):
    print(f"\n--- SHORTS PIPELINE ---")
    temp_files = []

    try:
        print("S1: Generating Shorts text (45s)...")
        text = generate_shorts_text(topic)
        print(f"   Done: {len(text)} characters\n")

        audio_path = os.path.join(TEMP_DIR, f"shorts_audio_{timestamp}.mp3")
        temp_files.append(audio_path)
        print("S2: Generating Shorts audio...")
        await generate_audio(text, audio_path)
        print(f"   Done\n")

        print("S3: Generating image prompts...")
        segments = generate_shorts_image_prompts(text)
        print(f"   Done: {len(segments)} segments\n")

        print("S4: Generating AI images (vertical)...")
        images = []
        for i, seg in enumerate(segments):
            img_path = os.path.join(TEMP_DIR, f"shorts_img_{timestamp}_{i}.jpg")
            print(f"   {i+1}/{len(segments)}: {seg['prompt'][:50]}...")
            success = download_image(seg["prompt"], img_path, seed=i*77)
            if success:
                images.append(img_path)
                temp_files.append(img_path)
            else:
                fallback_files = [os.path.join(BG_DIR, f) for f in os.listdir(BG_DIR) if f.endswith('.jpg')]
                if fallback_files:
                    images.append(random.choice(fallback_files))
        print(f"   Done: {len(images)} images\n")

        shorts_path = os.path.join(OUTPUT_DIR, f"shorts_{timestamp}.mp4")
        print("S5: Creating Shorts video...")
        generate_shorts_video(audio_path, images, shorts_path, category)

        print("S6: Uploading Shorts to YouTube...")
        from youtube_upload import upload_shorts
        shorts_id = upload_shorts(shorts_path, topic, main_video_id)

        for f in temp_files:
            try:
                os.remove(f)
            except:
                pass

        print(f"--- SHORTS DONE: https://youtube.com/shorts/{shorts_id} ---\n")
        return shorts_id

    except Exception as e:
        print(f"SHORTS ERROR: {e}")
        import traceback
        traceback.print_exc()
        for f in temp_files:
            try:
                os.remove(f)
            except:
                pass
