"""Claude AI service for parsing free-text customer descriptions into structured data."""

import json
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")

PARSE_SYSTEM_PROMPT = """Sen San Marcos Tanger Outlets'teki VAV kadin giyim magazasinin musteri kayit sistemisin.
Kullanici (magaza sahibi) serbest metin olarak bir musteri hakkinda bilgi yazacak. Turkce, Ingilizce veya karisik yazabilir.
Senin gorev bu metni yapilandirilmis JSON'a cevirmek.

Asagidaki JSON formatinda SADECE JSON dondur, baska hicbir sey yazma:

{
    "age_range": "18-25" | "25-35" | "35-45" | "45-55" | "55+" | null,
    "ethnicity": "hispanic" | "white" | "black" | "asian" | "middle_eastern" | "mixed_other" | null,
    "group_size": "tek" | "2_kisi" | "grup" | null,
    "looked_at": ["elbise", "bluz", "pantolon", "canta", "sapka", "aksesuar", "etek", "elbise", "ceket", "takim"] veya bos liste,
    "tried_on": true | false,
    "tried_count": sayi veya 0,
    "purchased": true | false,
    "purchased_items": ["urun adi ve adet"] veya bos liste,
    "price_segment": "indirimli" | "normal" | "premium" | "karisik" | null,
    "amount_range": "$1-25" | "$25-50" | "$50-100" | "$100-200" | "$200+" | null,
    "exact_amount": sayi veya null,
    "price_reaction": "sormadi" | "normal" | "pahali" | "pazarlik" | null,
    "mood": "memnun" | "kararsiz" | "mutsuz" | null,
    "time_spent_min": sayi veya null,
    "notes": "ekstra notlar veya orijinal metinden cikarilan detaylar"
}

KRITIK KURALLAR:

IRK/ETNISITE ALGILAMA:
- Hispanic/Latina: mexican, latina, hispanic, meksikali, porto rikolu, dominikli, kolombiyali, guatelamali, ispanyol kokenli
- White/Caucasian: amerikan, beyaz, alman, german, fransiz, french, italyan, avrupali, european, ingiliz, british, rus, russian, polonyali, irlanldali, kanadalı, avustralyali
- Black/African American: siyah, black, african american, afrikan, african, nigerian, jamaican, haitian
- Asian: cinli, chinese, japon, japanese, korean, koreli, vietnamli, filipinli, hindistanli, indian (dikkat: indian bazen native american olabilir, baglama bak), pakistanli, thai, taylandli
- Middle Eastern: turk, turkish, arab, arap, iranian, iranli, iraqi, syrian, suriyeli, lebanese, lubnanlı, israeli
- Mixed/Other: diger, biracial, mixed, native american, indigenous
- Milliyet yazildiysa (fransiz, alman, turk, meksikali vb.) uygun ethnicity kategorisine esle
- ASLA null birakma eger herhangi bir ipucu varsa

GRUP BOYUTU:
- "tek", "yalniz", "bir kisi" = "tek"
- "arkadasiyla", "annesiyle", "2 kisi", "iki kisi", "cifti" = "2_kisi"
- "3 kisi", "grup", "aile", "3+", "arkadaslariyla" = "grup"
- Sayi belirtilmisse ona gore sec

URUN KATEGORILERI:
- looked_at: musteri neye BAKTI (goz atti, ilgilendi, ellerine aldi)
- Birden fazla kategori olabilir: ["elbise", "pantolon", "canta"]
- Eger sadece satin aldiklari belirtilmis ve baska bir seye baktiginden bahsedilmemisse, satin aldigi kategoriyi looked_at'a da ekle
- Urun isimleri: etek (skirt), elbise (dress), bluz (blouse/top), pantolon (pants), canta (bag/purse), sapka (hat), aksesuar (accessory), ceket (jacket), takim (set/outfit)

DENEME (TRIED_ON):
- "denedi", "kabine girdi", "fitting room", "uzerinde denedi", "giydi" = tried_on: true
- tried_count: kac FARKLI urun denediyse o sayi. "2 tane denedi" = 2, "kabine girip denediler" = en az 2 (birden fazla oldugu anlasiliyor)
- Grup olarak denedilerse, toplam denenen urun sayisini tahmin et

SATIN ALMA:
- purchased_items: ne aldiysa adet ile yaz. "4 tane etek" = ["4 etek"], "1 pantolon 2 bluz" = ["1 pantolon", "2 bluz"]
- exact_amount: toplam odenen tutar (dolar). "50 dolar" = 50, "$35" = 35, "50 dolar civari" = 50
- price_segment: "indirimli" = sale/discount/promosyon/buy X get Y free. "normal" = normal fiyat. "premium" = pahali urun. "karisik" = hem indirimli hem normal
- amount_range: exact_amount'a gore otomatik sec

FIYAT TEPKISI (satin almadiysa):
- "pahali buldu", "pahali dedi", "fiyata baktı alamadı" = "pahali"
- "pazarlik istedi", "indirim istedi" = "pazarlik"
- Hicbir sey demediyse = "sormadi"

RUH HALI:
- Satin aldiysa ve olumsuz bir sey belirtilmediyse = "memnun"
- "kararsiz kaldi", "dusunecegim dedi", "emin degildi" = "kararsiz"
- "begenmedi", "mutsuz", "sikayetci" = "mutsuz"
- Satin almadiysa ama olumsuz bir sey belirtilmediyse = "kararsiz"

NOTES:
- Musteri hakkinda ekstra bilgiler: nereden geldi, ne dedi, ozel durum, promosyon kullanimi vb.
- Kisa ve oz yaz

SADECE JSON dondur, aciklama yazma."""


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
