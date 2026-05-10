import subprocess
import os
import random
import math
from PIL import Image, ImageDraw
import json

PARTICLES_DIR = r"C:\Users\excat\Desktop\Youtube DOSYALARI\historia\particles"
FRAMES_DIR = os.path.join(PARTICLES_DIR, "frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

CATEGORY_PARTICLES = {
    "antik": "ates",
    "savas": "ates",
    "gizem": "gizem",
    "ortacag": "duman",
    "deniz": "deniz"
}

PARTICLE_CONFIGS = {
    "ates": {
        "colors": [(255, 100, 0), (255, 50, 0), (255, 200, 0), (255, 150, 0)],
        "count": 120,
        "min_size": 2,
        "max_size": 5,
        "speed_x": 0.3,
        "speed_y": -1.5,
        "wobble": 0.5,
        "alpha": 180
    },
    "gizem": {
        "colors": [(150, 150, 255), (200, 200, 255), (255, 255, 255), (180, 180, 220)],
        "count": 80,
        "min_size": 1,
        "max_size": 3,
        "speed_x": 0.1,
        "speed_y": -0.5,
        "wobble": 0.3,
        "alpha": 120
    },
    "kar": {
        "colors": [(255, 255, 255), (200, 220, 255), (220, 240, 255)],
        "count": 150,
        "min_size": 2,
        "max_size": 5,
        "speed_x": 0.2,
        "speed_y": 1.0,
        "wobble": 0.4,
        "alpha": 160
    },
    "duman": {
        "colors": [(100, 100, 100), (120, 120, 120), (80, 80, 80)],
        "count": 50,
        "min_size": 8,
        "max_size": 20,
        "speed_x": 0.1,
        "speed_y": -0.3,
        "wobble": 0.2,
        "alpha": 60
    },
    "deniz": {
        "colors": [(100, 180, 255), (50, 150, 255), (150, 200, 255)],
        "count": 90,
        "min_size": 1,
        "max_size": 4,
        "speed_x": 0.3,
        "speed_y": -0.8,
        "wobble": 0.6,
        "alpha": 140
    }
}

def generate_particle_video(name, duration_seconds=700, fps=25):
    config = PARTICLE_CONFIGS[name]
    output_path = os.path.join(PARTICLES_DIR, f"{name}.mp4")
    
    if os.path.exists(output_path):
        print(f"  {name}.mp4 already exists, skipping")
        return output_path
    
    print(f"  Generating {name} particles ({duration_seconds}s)...")
    
    # Parcacikilari baslangic konumlarinda olustur
    particles = []
    for _ in range(config["count"]):
        particles.append({
            "x": random.uniform(0, 1920),
            "y": random.uniform(0, 1080),
            "vx": random.uniform(-config["speed_x"], config["speed_x"]),
            "vy": random.uniform(config["speed_y"]*0.5, config["speed_y"]*1.5),
            "size": random.randint(config["min_size"], config["max_size"]),
            "color": random.choice(config["colors"]),
            "phase": random.uniform(0, math.pi*2),
            "life": random.uniform(0, 1)
        })
    
    # Sadece 125 frame uret (5 saniye, loop yapacak)
    loop_frames = 5 * fps
    frame_paths = []
    
    for frame_idx in range(loop_frames):
        t = frame_idx / fps
        
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        for p in particles:
            wobble_x = math.sin(t * 2 + p["phase"]) * config["wobble"] * 20
            x = (p["x"] + p["vx"] * frame_idx + wobble_x) % 1920
            y = (p["y"] + p["vy"] * frame_idx) % 1080
            
            size = p["size"]
            color = p["color"] + (config["alpha"],)
            
            draw.ellipse(
                [(x - size, y - size), (x + size, y + size)],
                fill=color
            )
        
        frame_path = os.path.join(FRAMES_DIR, f"{name}_{frame_idx:04d}.png")
        img.save(frame_path, "PNG")
        frame_paths.append(frame_path)
    
    # 5 saniyelik loop video olustur
    loop_path = os.path.join(PARTICLES_DIR, f"{name}_loop.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(FRAMES_DIR, f"{name}_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-t", "5",
        loop_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    
    # Loop videosunu duration kadar uzat
    cmd2 = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", loop_path,
        "-t", str(duration_seconds),
        "-c:v", "libx264",
        "-pix_fmt", "yuva420p",
        output_path
    ]
    subprocess.run(cmd2, check=True, capture_output=True)
    
    # Frame dosyalarini temizle
    for fp in frame_paths:
        try:
            os.remove(fp)
        except:
            pass
    try:
        os.remove(loop_path)
    except:
        pass
    
    print(f"  Done: {name}.mp4")
    return output_path

print("Generating particle overlays...")
for name in PARTICLE_CONFIGS.keys():
    generate_particle_video(name, duration_seconds=700)

with open(os.path.join(PARTICLES_DIR, "mapping.json"), "w") as f:
    json.dump(CATEGORY_PARTICLES, f)

print("\nAll particles generated!")
print("Files in particles folder:")
for f in os.listdir(PARTICLES_DIR):
    print(f"  {f}")
