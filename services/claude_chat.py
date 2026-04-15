"""Claude AI chat service for general conversation with store owner."""

import os
from anthropic import Anthropic
from collections import defaultdict

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")

CHAT_SYSTEM_PROMPT = """Sen VAV kadin giyim magazasinin AI asistanisin. Magaza San Marcos Tanger Outlets'te (Texas, ABD).

Magaza sahibi Bekir ve esi seninle konusacak. Turkce konusuyorsun.

Yardimci olabilecegin konular:
- Satis stratejileri ve taktikleri
- Musteri iliskileri ve hizmet
- Perakende sektoru tavsiyeleri
- Fiyatlandirma stratejileri
- Sosyal medya ve pazarlama fikirleri
- Magaza duzeni ve gorsel merchandising
- Stok yonetimi
- Outlet alisveris merkezi dinamikleri
- Rekabet analizi
- Promosyon ve kampanya fikirleri

Kisa, pratik ve aksiyon odakli cevaplar ver. Gereksiz uzatma. Magazanin yeni acildigini ve kurulum asamasinda oldugunu bil.

Eger kullanici musteri bilgisi yazarsa (yas, irk, ne aldı vb.) onu uyar: "Bu bir musteri kaydi gibi gorunuyor. /musteri moduna gec veya direkt musteri bilgisini yaz."
"""

# In-memory chat history per user
chat_history: dict[int, list[dict]] = defaultdict(list)
MAX_HISTORY = 20


def get_chat_response(chat_id: int, message: str) -> str:
    """Get a conversational response from Claude."""
    chat_history[chat_id].append({"role": "user", "content": message})

    # Keep history manageable
    if len(chat_history[chat_id]) > MAX_HISTORY:
        chat_history[chat_id] = chat_history[chat_id][-MAX_HISTORY:]

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=CHAT_SYSTEM_PROMPT,
            messages=chat_history[chat_id],
        )
        reply = response.content[0].text
        chat_history[chat_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        print(f"Chat error: {e}")
        return "❌ Bir hata olustu. Tekrar dene."


def clear_chat_history(chat_id: int):
    """Clear chat history for a user."""
    chat_history[chat_id] = []
