"""Vercel serverless webhook endpoint for Telegram bot."""

import asyncio
import json
import os
from http.server import BaseHTTPRequestHandler

from dotenv import load_dotenv

load_dotenv()

from telegram import Bot, Update
from bot.handlers import handle_update


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            update_data = json.loads(body)
            asyncio.run(process_update(update_data))
        except Exception as e:
            print(f"Error processing update: {e}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps({"status": "VAV Customer Tracker Bot is running"}).encode()
        )


async def process_update(update_data: dict):
    bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
    update = Update.de_json(update_data, bot)
    await handle_update(bot, update)
