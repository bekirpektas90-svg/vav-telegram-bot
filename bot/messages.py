"""Turkish message templates for the VAV bot."""

WELCOME = """👋 Hosgeldin VAV Customer Tracker'a!

Bu bot ile magazaya gelen musterileri kayit altina alabilirsin ve AI asistanla konusabilirsin.

📝 MUSTERI KAYDI:
• Direkt yaz: "30lu hispanic kadin, elbise denedi, almadi"
• /yeni — Butonlarla adim adim gir

🤖 AI ASISTAN:
• /ai — AI sohbet modunu ac (strateji, tavsiye, soru)
• ?soru — Tek seferlik AI sorusu

📊 RAPORLAR:
• /bugun — Gunluk ozet
• /hafta — Haftalik trend
• /analiz — AI derinlemesine analiz
• /son — Son 5 kayit
• /sil — Son kaydi sil

Haydi baslayalim! 🚀"""

HELP = """📋 VAV Bot Komutlari:

MUSTERI KAYDI:
/yeni — Detayli musteri girisi (butonlarla)
/musteri — Musteri kayit moduna don
/son — Son 5 musteri kaydini goster
/sil — Son girdiyi sil

AI ASISTAN:
/ai — AI sohbet modunu ac
/musteri — AI modundan cik
?soru — Tek seferlik AI sorusu (ornek: ?bugun nasil satis yapabilirim)

RAPORLAR:
/bugun — Bugunun ozet raporu
/hafta — Haftalik trend raporu
/analiz — AI destekli derin analiz

/help — Bu yardim mesaji

💡 Hizli musteri girisi: Komut yazmadan direkt musteri bilgisini yaz!
Ornek: "25 yasinda asian kiz, canta aldi 35$, memnundu"
"""

NEW_ENTRY_START = "👤 Yeni musteri kaydi baslatiliyor...\n\nYas araligi?"

AGE_QUESTION = "👤 Yas araligi?"
ETHNICITY_QUESTION = "🌍 Irk / Etnisite?"
GROUP_QUESTION = "👥 Kac kisi geldi?"
LOOKED_AT_QUESTION = "👗 Ne bakti? (Birden fazla secebilirsin, bitince 'Devam' tikla)"
TRIED_QUESTION = "👚 Urun denedi mi?"
PURCHASED_QUESTION = "🛍️ Satin aldi mi?"
PRICE_SEGMENT_QUESTION = "💲 Fiyat segmenti?"
AMOUNT_QUESTION = "💵 Ne kadar harcadi?"
PRICE_REACTION_QUESTION = "💸 Fiyat tepkisi ne oldu?"
MOOD_QUESTION = "😊 Musteri ruh hali nasıldi?"
NOTES_QUESTION = "📝 Ekstra not? (Yaz veya 'Gec' tikla)"

RECORD_SAVED = "✅ Musteri kaydi basariyla kaydedildi!"
RECORD_DELETED = "🗑️ Son musteri kaydin silindi."
NO_RECORDS = "📭 Henuz musteri kaydi yok."
NO_RECORD_TO_DELETE = "❌ Silinecek kayit bulunamadi."
ERROR_MESSAGE = "❌ Bir hata olustu. Lutfen tekrar dene."

ANALYZING = "🔄 Analiz ediliyor..."
GENERATING_REPORT = "🔄 Rapor olusturuluyor..."
