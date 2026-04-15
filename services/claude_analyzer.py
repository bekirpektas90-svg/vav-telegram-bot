"""Claude AI service for generating customer analytics and reports."""

import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")


def generate_daily_report(customers: list[dict]) -> str:
    """Generate a daily summary report from customer records."""
    if not customers:
        return "📊 Bugun henuz musteri kaydi yok."

    total = len(customers)
    purchased = [c for c in customers if c.get("purchased")]
    purchase_count = len(purchased)
    purchase_rate = round(purchase_count / total * 100) if total > 0 else 0

    # Ciro hesapla
    total_revenue = sum(
        float(c.get("exact_amount") or 0) for c in purchased
    )

    # Irk dagilimi
    ethnicity_stats = {}
    for c in customers:
        eth = c.get("ethnicity") or "belirtilmedi"
        if eth not in ethnicity_stats:
            ethnicity_stats[eth] = {"total": 0, "purchased": 0, "revenue": 0}
        ethnicity_stats[eth]["total"] += 1
        if c.get("purchased"):
            ethnicity_stats[eth]["purchased"] += 1
            ethnicity_stats[eth]["revenue"] += float(c.get("exact_amount") or 0)

    # En cok bakilan kategoriler
    category_counts = {}
    for c in customers:
        for item in (c.get("looked_at") or []):
            category_counts[item] = category_counts.get(item, 0) + 1

    # En cok satilan
    sold_counts = {}
    for c in purchased:
        for item in (c.get("purchased_items") or []):
            sold_counts[item] = sold_counts.get(item, 0) + 1

    # Fiyat tepkisi
    price_reactions = {}
    for c in customers:
        pr = c.get("price_reaction") or "belirtilmedi"
        price_reactions[pr] = price_reactions.get(pr, 0) + 1

    # Kaydeden
    recorders = {}
    for c in customers:
        rec = c.get("recorded_by", "?")
        recorders[rec] = recorders.get(rec, 0) + 1

    # Rapor olustur
    lines = [f"📊 VAV Gunluk Rapor\n"]
    lines.append(f"👥 Toplam musteri: {total}")
    lines.append(f"💰 Satis yapilan: {purchase_count} (%{purchase_rate})")
    if total_revenue > 0:
        lines.append(f"💵 Toplam ciro: ${total_revenue:.0f}")

    # Irk dagilimi
    eth_labels = {
        "hispanic": "Hispanic",
        "white": "White",
        "black": "Black",
        "asian": "Asian",
        "middle_eastern": "Middle Eastern",
        "mixed_other": "Mixed/Other",
        "belirtilmedi": "Belirtilmedi",
    }
    if ethnicity_stats:
        lines.append("\n📈 Irk Dagilimi:")
        for eth, stats in sorted(
            ethnicity_stats.items(), key=lambda x: x[1]["total"], reverse=True
        ):
            label = eth_labels.get(eth, eth)
            rev = f" — ${stats['revenue']:.0f}" if stats["revenue"] > 0 else ""
            lines.append(
                f"  {label}: {stats['total']} ({stats['purchased']} aldi){rev}"
            )

    # Kategoriler
    if category_counts:
        top_cat = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        lines.append(
            f"\n👗 En cok bakilan: {', '.join(f'{k} ({v}x)' for k, v in top_cat)}"
        )

    if sold_counts:
        top_sold = sorted(sold_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        lines.append(
            f"🛍️ En cok satilan: {', '.join(f'{k} ({v}x)' for k, v in top_sold)}"
        )

    # Fiyat tepkisi
    pahali_count = price_reactions.get("pahali", 0)
    if pahali_count > 0 and total > 0:
        lines.append(f"\n💸 Pahali bulan: %{round(pahali_count / total * 100)}")

    # Kaydeden
    if recorders:
        rec_str = ", ".join(f"{k}: {v}" for k, v in recorders.items())
        lines.append(f"\n📝 Kaydeden: {rec_str}")

    return "\n".join(lines)


def generate_weekly_report(customers: list[dict]) -> str:
    """Generate a weekly trend report from customer records."""
    if not customers:
        return "📊 Bu hafta henuz musteri kaydi yok."

    from collections import defaultdict
    from datetime import datetime

    # Gun bazli gruplama
    daily = defaultdict(list)
    for c in customers:
        if c.get("recorded_at"):
            dt = datetime.fromisoformat(c["recorded_at"].replace("Z", "+00:00"))
            day_name = ["Pzt", "Sal", "Car", "Per", "Cum", "Cmt", "Paz"][dt.weekday()]
            day_key = dt.strftime("%m/%d")
            daily[f"{day_name} {day_key}"].append(c)

    total = len(customers)
    purchased = [c for c in customers if c.get("purchased")]
    total_revenue = sum(float(c.get("exact_amount") or 0) for c in purchased)

    lines = [f"📊 VAV Haftalik Trend\n"]
    lines.append(f"👥 Toplam musteri: {total}")
    lines.append(f"💰 Toplam satis: {len(purchased)} (%{round(len(purchased)/total*100) if total else 0})")
    if total_revenue > 0:
        lines.append(f"💵 Toplam ciro: ${total_revenue:.0f}")

    # Gun bazli grafik
    if daily:
        lines.append("\n📈 Gun bazli:")
        max_count = max(len(v) for v in daily.values()) if daily else 1
        for day, custs in sorted(daily.items()):
            bar_len = round(len(custs) / max(max_count, 1) * 10)
            bar = "█" * bar_len + "░" * (10 - bar_len)
            day_purchased = len([c for c in custs if c.get("purchased")])
            day_revenue = sum(float(c.get("exact_amount") or 0) for c in custs if c.get("purchased"))
            rev_str = f" ${day_revenue:.0f}" if day_revenue > 0 else ""
            lines.append(f"  {day}: {bar} {len(custs)} ({day_purchased} satis){rev_str}")

    # Irk bazli trend
    eth_data = defaultdict(lambda: {"total": 0, "purchased": 0, "top_items": defaultdict(int)})
    for c in customers:
        eth = c.get("ethnicity") or "belirtilmedi"
        eth_data[eth]["total"] += 1
        if c.get("purchased"):
            eth_data[eth]["purchased"] += 1
        for item in (c.get("looked_at") or []):
            eth_data[eth]["top_items"][item] += 1

    eth_labels = {
        "hispanic": "Hispanic", "white": "White", "black": "Black",
        "asian": "Asian", "middle_eastern": "Middle Eastern",
        "mixed_other": "Mixed/Other", "belirtilmedi": "Belirtilmedi",
    }

    if eth_data:
        lines.append("\n🎯 Irk bazli:")
        for eth, data in sorted(eth_data.items(), key=lambda x: x[1]["total"], reverse=True):
            label = eth_labels.get(eth, eth)
            top_items = sorted(data["top_items"].items(), key=lambda x: x[1], reverse=True)[:2]
            items_str = ", ".join(k for k, v in top_items) if top_items else "-"
            rate = round(data["purchased"] / data["total"] * 100) if data["total"] > 0 else 0
            lines.append(f"  {label}: {data['total']} musteri, %{rate} satis → {items_str}")

    return "\n".join(lines)


def generate_ai_analysis(customers: list[dict]) -> str:
    """Generate deep AI-powered customer analysis using Claude."""
    if not customers:
        return "📊 Analiz icin yeterli veri yok."

    # Veriyi ozetle
    summary_lines = []
    for c in customers:
        parts = []
        if c.get("ethnicity"):
            parts.append(c["ethnicity"])
        if c.get("age_range"):
            parts.append(c["age_range"])
        if c.get("group_size"):
            parts.append(c["group_size"])
        if c.get("looked_at"):
            parts.append(f"bakti:{','.join(c['looked_at'])}")
        if c.get("purchased"):
            amt = c.get("exact_amount") or c.get("amount_range") or "?"
            parts.append(f"aldi:${amt}")
            if c.get("price_segment"):
                parts.append(c["price_segment"])
        else:
            parts.append("almadi")
            if c.get("price_reaction"):
                parts.append(c["price_reaction"])
        if c.get("mood"):
            parts.append(c["mood"])
        if c.get("notes"):
            parts.append(f"not:{c['notes']}")
        if c.get("recorded_at"):
            parts.append(c["recorded_at"][:10])
        summary_lines.append(" | ".join(parts))

    data_text = "\n".join(summary_lines)

    analysis_prompt = f"""Sen bir perakende magaza danismanisin. Asagida San Marcos Tanger Outlets'teki VAV kadin giyim magazasinin musteri kayitlari var.

Bu verileri analiz et ve su basliklarda Turkce rapor yaz:

1. 🎯 MUSTERI PROFILI: Ana musteri kitlesini tanimla (yas, irk, alisveris davranisi)
2. 💰 FIYATLANDIRMA: Fiyat hassasiyeti analizi, hangi irk/yas grubu ne harcıyor
3. 👗 URUN ONERILERI: Hangi kategoriler populer, stok onerileri
4. 📱 PAZARLAMA ONERILERI: Hangi kitleye nasil ulasilmali
5. ⚠️ DIKKAT EDILMESI GEREKENLER: Olumsuz trendler veya firsatlar
6. 📈 GENEL DEGERLENDIRME: Kisa ozet ve aksiyon onerileri

Veri ({len(customers)} musteri kaydi):
{data_text}

Raporu kisa ve aksiyon odakli yaz. Emoji kullan. Turkce yaz."""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": analysis_prompt}],
        )
        return f"🧠 VAV AI Analiz Raporu\n\n{response.content[0].text}"
    except Exception as e:
        print(f"Error generating AI analysis: {e}")
        return "❌ Analiz olusturulurken hata olustu. Lutfen tekrar deneyin."
