def select_topic_and_keywords():
    client = anthropic.Anthropic(api_key=API_KEY)
    print("   - AI generating unique topic...")
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": """Wymy?l oryginalny i intryguj?cy temat historyczny.

ZASADY:
- Temat ma?o znany, zaskakuj?cy, tajemniczy
- Prawdziwe wydarzenie historyczne
- Intryguj?cy tytu? kt?ry przyci?ga uwag?
- Nie powtarzaj popularnych temat?w

Kategorie ambient:
- antik: staro?ytne cywilizacje, Egipt, Grecja, Rzym, Majowie
- savas: wojny, bitwy, podboje, imperia
- gizem: tajemnice, zagini?cia, przepowiednie, kl?twy
- ortacag: ?redniowiecze, krzy?owcy, zamki
- deniz: odkrycia morskie, Wikingowie, wyprawy

Zwr?? TYLKO JSON, zero komentarzy:
{
  "topic": "intryguj?cy tytu? tematu po polsku",
  "keywords": ["english keyword1", "english keyword2", "english keyword3"],
  "category": "jedna z: antik, savas, gizem, ortacag, deniz"
}"""
        }]
    )
    raw = message.content[0].text.strip().replace("`json", "").replace("`", "").strip()
    data = json.loads(raw)
    return data["topic"], data["keywords"], data["category"]
