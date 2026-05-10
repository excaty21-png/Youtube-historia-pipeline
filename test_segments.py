import anthropic
import json
from dotenv import load_dotenv
import os

load_dotenv(r"C:\Users\excat\Desktop\Youtube DOSYALARI\historia\.env")
API_KEY = os.environ.get("ANTHROPIC_API_KEY")

test_text = """Czy wiesz, ?e wielka cywilizacja Maj?w... znikn??a w ci?gu zaledwie kilku pokole??
Przez setki lat budowali wielkie miasta... ?wi?tynie si?gaj?ce nieba... i skomplikowane kalendarze.
A potem... w ci?gu zaledwie stu lat... wszystko znikn??o w d?ungli.
Historycy do dzi? nie wiedz? dlaczego... Czy by?a to susza... wojny... czy mo?e co? innego?
Jutro opowiem ci kolejn? histori?... Je?li chcesz wi?cej, subskrybuj Historia do Poduszki..."""

client = anthropic.Anthropic(api_key=API_KEY)
message = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=1000,
    messages=[{
        "role": "user",
        "content": f"""Poni?szy tekst b?dzie czytany przez lektora. 
Podziel go na fragmenty po oko?o 20 sekund czytania (oko?o 40-50 s??w ka?dy).
Dla ka?dego fragmentu napisz prompt po angielsku do generowania obrazu AI.

Prompt musi by?:
- Po angielsku
- Opisywa? sceneri? pasuj?c? do tre?ci fragmentu
- Styl: cinematic digital illustration, dark atmospheric, historical
- Kr?tki: maksymalnie 15 s??w

Zwr?? TYLKO JSON, zero komentarzy:
{{
  "segments": [
    {{
      "text": "fragment tekstu",
      "prompt": "image prompt in english"
    }}
  ]
}}

Tekst:
{test_text}"""
    }]
)

raw = message.content[0].text.strip().replace("`json", "").replace("`", "").strip()
data = json.loads(raw)

for i, seg in enumerate(data["segments"]):
    print(f"Segment {i+1}:")
    print(f"  Text: {seg['text'][:60]}...")
    print(f"  Prompt: {seg['prompt']}")
    print()
