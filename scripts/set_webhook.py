"""Register the Telegram webhook URL after deploying to Vercel."""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()


def set_webhook(vercel_url: str):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not set in .env file")
        sys.exit(1)

    webhook_url = f"{vercel_url.rstrip('/')}/api/webhook"
    api_url = f"https://api.telegram.org/bot{token}/setWebhook"

    response = requests.post(api_url, json={"url": webhook_url})
    result = response.json()

    if result.get("ok"):
        print(f"✅ Webhook basariyla ayarlandi: {webhook_url}")
    else:
        print(f"❌ Webhook ayarlanamadi: {result.get('description')}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanim: python scripts/set_webhook.py <vercel-url>")
        print("Ornek: python scripts/set_webhook.py https://vav-bot.vercel.app")
        sys.exit(1)
    set_webhook(sys.argv[1])
