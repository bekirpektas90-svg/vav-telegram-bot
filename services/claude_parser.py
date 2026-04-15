"""Claude AI service for parsing free-text customer descriptions into structured data."""

import json
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")

PARSE_SYSTEM_PROMPT = """Sen bir perakende magaza musteri kayit sistemisin.
Kullanici serbest metin olarak bir musteri hakkinda bilgi yazacak.
Senin gorev bu metni yapilandirilmis JSON'a cevirmek.

Asagidaki JSON formatinda SADECE JSON dondur, baska hicbir sey yazma:

{
    "age_range": "18-25" | "25-35" | "35-45" | "45-55" | "55+" | null,
    "ethnicity": "hispanic" | "white" | "black" | "asian" | "middle_eastern" | "mixed_other" | null,
    "group_size": "tek" | "2_kisi" | "grup" | null,
    "looked_at": ["elbise", "bluz", "pantolon", "canta", "sapka", "aksesuar"] veya bos liste,
    "tried_on": true | false,
    "tried_count": sayi veya 0,
    "purchased": true | false,
    "purchased_items": ["urun adi"] veya bos liste,
    "price_segment": "indirimli" | "normal" | "premium" | "karisik" | null,
    "amount_range": "$1-25" | "$25-50" | "$50-100" | "$100-200" | "$200+" | null,
    "exact_amount": sayi veya null,
    "price_reaction": "sormadi" | "normal" | "pahali" | "pazarlik" | null,
    "mood": "memnun" | "kararsiz" | "mutsuz" | null,
    "time_spent_min": sayi veya null,
    "notes": "ekstra notlar veya orijinal metinden cikarilan detaylar"
}

Kurallar:
- Metinde belirtilmeyen alanlari null veya bos birak
- Irk/etnisite icin ipuclarina dikkat et: latina/mexican/hispanic, white/caucasian, black/african american, asian, middle eastern/arab/turkish
- Fiyat bilgisi varsa exact_amount'a dolar cinsinden yaz
- Birden fazla urun kategorisine bakmis olabilir, hepsini looked_at'a ekle
- notes alanina metinden cikardigin ama yapiya uymayan ekstra bilgileri yaz
- SADECE JSON dondur, aciklama yazma"""


def parse_customer_text(text: str) -> dict | None:
    """Parse free-text customer description into structured data using Claude."""
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=PARSE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}],
        )
        raw = response.content[0].text.strip()
        # Extract JSON if wrapped in markdown code blocks
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        return json.loads(raw)
    except (json.JSONDecodeError, IndexError, Exception) as e:
        print(f"Error parsing customer text: {e}")
        return None


def format_parsed_result(data: dict) -> str:
    """Format parsed customer data into a readable Telegram message."""
    lines = ["✅ Musteri kaydedildi!\n"]

    # Demografik
    demo_parts = []
    if data.get("age_range"):
        demo_parts.append(f"Yas: {data['age_range']}")
    if data.get("ethnicity"):
        eth_labels = {
            "hispanic": "Hispanic",
            "white": "White",
            "black": "Black",
            "asian": "Asian",
            "middle_eastern": "Middle Eastern",
            "mixed_other": "Mixed/Other",
        }
        demo_parts.append(eth_labels.get(data["ethnicity"], data["ethnicity"]))
    if data.get("group_size"):
        grp_labels = {"tek": "Tek", "2_kisi": "2 kisi", "grup": "Grup 3+"}
        demo_parts.append(grp_labels.get(data["group_size"], data["group_size"]))
    if demo_parts:
        lines.append(f"👤 {' | '.join(demo_parts)}")

    # Ne bakti
    if data.get("looked_at"):
        items = ", ".join(data["looked_at"])
        lines.append(f"👗 Bakti: {items}")

    # Denedi mi
    if data.get("tried_on"):
        count = data.get("tried_count", 0)
        lines.append(f"👚 Denedi: {count} adet" if count else "👚 Denedi")

    # Satin alma
    if data.get("purchased"):
        parts = []
        if data.get("purchased_items"):
            parts.append(", ".join(data["purchased_items"]))
        if data.get("exact_amount"):
            parts.append(f"${data['exact_amount']}")
        elif data.get("amount_range"):
            parts.append(data["amount_range"])
        if data.get("price_segment"):
            seg_labels = {
                "indirimli": "Indirimli",
                "normal": "Normal fiyat",
                "premium": "Premium",
                "karisik": "Karisik",
            }
            parts.append(seg_labels.get(data["price_segment"], data["price_segment"]))
        lines.append(f"💰 Satin aldi: {' | '.join(parts)}" if parts else "💰 Satin aldi")
    else:
        lines.append("❌ Satin almadi")
        if data.get("price_reaction"):
            pr_labels = {
                "sormadi": "Fiyat sormadi",
                "normal": "Normal buldu",
                "pahali": "Pahali buldu",
                "pazarlik": "Pazarlik istedi",
            }
            lines.append(
                f"💸 {pr_labels.get(data['price_reaction'], data['price_reaction'])}"
            )

    # Ruh hali
    if data.get("mood"):
        mood_emojis = {"memnun": "😊", "kararsiz": "😐", "mutsuz": "😞"}
        emoji = mood_emojis.get(data["mood"], "")
        lines.append(f"{emoji} {data['mood'].capitalize()}")

    # Not
    if data.get("notes"):
        lines.append(f"\n📝 {data['notes']}")

    return "\n".join(lines)
