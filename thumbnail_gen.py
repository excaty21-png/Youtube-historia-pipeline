import requests
import time
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
import google.generativeai as genai
from dotenv import load_dotenv
import json

if os.name == 'nt':
    load_dotenv(r"C:\Users\excat\Desktop\Youtube DOSYALARI\historia\.env")
    BASE_DIR = r"C:\Users\excat\Desktop\Youtube DOSYALARI\historia"
else:
    load_dotenv()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
_model = genai.GenerativeModel("gemini-2.5-pro")
FONT_PATH = os.path.join(BASE_DIR, "fonts", "Montserrat-ExtraBold.ttf")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

def download_font_if_missing():
    os.makedirs(os.path.dirname(FONT_PATH), exist_ok=True)
    if not os.path.exists(FONT_PATH):
        print("   - Downloading font...")
        url = "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-ExtraBold.ttf"
        response = requests.get(url, timeout=30)
        with open(FONT_PATH, "wb") as f:
            f.write(response.content)
        print("   - Font downloaded!")

def generate_thumbnail_text(topic):
    response = _model.generate_content(f"""Dla tego tematu historycznego napisz krotki tytul na miniaturke YouTube.

Temat: {topic}

ZASADY:
- Maksymalnie 4 slowa
- Bardzo intrygujace, tajemnicze
- Po polsku
- TYLKO tytul, zero komentarzy
- Przyklad: "ZAGINELI W JEDNA NOC" lub "SEKRET KTOREGO NIE ZNASZ"

Zwroc TYLKO tytul.""")
    return response.text.strip().upper()

def get_background_image(topic):
    prompt = f"historical scene {topic}, cinematic, atmospheric, detailed, professional photography style, no text"
    for attempt in range(3):
        try:
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1280&height=720&nologo=true&seed=99"
            response = requests.get(url, timeout=120)
            if len(response.content) > 10000:
                return Image.open(BytesIO(response.content)).convert("RGB")
        except:
            time.sleep(5)
    return None

def create_thumbnail(topic, output_path):
    download_font_if_missing()
    print(f"   - Generating thumbnail text...")
    title_text = generate_thumbnail_text(topic)
    print(f"   - Title: {title_text}")

    print(f"   - Downloading background...")
    bg = get_background_image(topic)
    if bg is None:
        bg = Image.new("RGB", (1280, 720), color=(20, 20, 40))

    bg = bg.resize((1280, 720))

    # Karanlik overlay ekle - yazı okunabilsin
    overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    # Alt kisma gradient overlay
    for i in range(300):
        alpha = int((i / 300) * 180)
        draw_overlay.rectangle([(0, 720-300+i), (1280, 720-300+i+1)], fill=(0, 0, 0, alpha))

    # Ust kisma hafif overlay
    for i in range(150):
        alpha = int((1 - i/150) * 100)
        draw_overlay.rectangle([(0, i), (1280, i+1)], fill=(0, 0, 0, alpha))

    bg_rgba = bg.convert("RGBA")
    bg_rgba = Image.alpha_composite(bg_rgba, overlay)
    bg = bg_rgba.convert("RGB")

    draw = ImageDraw.Draw(bg)

    # Ana baslik yazisi
    try:
        font_large = ImageFont.truetype(FONT_PATH, 90)
        font_small = ImageFont.truetype(FONT_PATH, 36)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Baslik - orta alt
    words = title_text.split()
    if len(words) > 2:
        line1 = " ".join(words[:len(words)//2])
        line2 = " ".join(words[len(words)//2:])
    else:
        line1 = title_text
        line2 = ""

    # Golge efekti - siyah
    for offset in [(3,3), (-3,3), (3,-3), (-3,-3)]:
        if line2:
            bbox1 = draw.textbbox((0,0), line1, font=font_large)
            w1 = bbox1[2] - bbox1[0]
            draw.text(((1280-w1)//2 + offset[0], 480 + offset[1]), line1, font=font_large, fill=(0,0,0))
            bbox2 = draw.textbbox((0,0), line2, font=font_large)
            w2 = bbox2[2] - bbox2[0]
            draw.text(((1280-w2)//2 + offset[0], 580 + offset[1]), line2, font=font_large, fill=(0,0,0))
        else:
            bbox1 = draw.textbbox((0,0), line1, font=font_large)
            w1 = bbox1[2] - bbox1[0]
            draw.text(((1280-w1)//2 + offset[0], 530 + offset[1]), line1, font=font_large, fill=(0,0,0))

    # Sari/altin ana yazi
    if line2:
        bbox1 = draw.textbbox((0,0), line1, font=font_large)
        w1 = bbox1[2] - bbox1[0]
        draw.text(((1280-w1)//2, 480), line1, font=font_large, fill=(255, 215, 0))
        bbox2 = draw.textbbox((0,0), line2, font=font_large)
        w2 = bbox2[2] - bbox2[0]
        draw.text(((1280-w2)//2, 580), line2, font=font_large, fill=(255, 215, 0))
    else:
        bbox1 = draw.textbbox((0,0), line1, font=font_large)
        w1 = bbox1[2] - bbox1[0]
        draw.text(((1280-w1)//2, 530), line1, font=font_large, fill=(255, 215, 0))

    # Marka ismi - sol alt
    brand_text = "Historia do Poduszki"
    draw.text((30, 670), brand_text, font=font_small, fill=(255, 255, 255, 200))

    # Sol taraf - altin cizgi
    draw.rectangle([(20, 20), (28, 700)], fill=(255, 215, 0))

    bg.save(output_path, "JPEG", quality=95)
    print(f"   - Thumbnail saved: {output_path}")
    return title_text

if __name__ == "__main__":
    os.makedirs(TEMP_DIR, exist_ok=True)
    output = os.path.join(TEMP_DIR, "thumbnail_test.jpg")
    create_thumbnail("Tajemnica Zaginiecia Majow", output)
    print("Done! Check temp/thumbnail_test.jpg")
