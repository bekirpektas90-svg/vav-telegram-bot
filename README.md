# VAV Customer Tracker Bot

Telegram bot for tracking and analyzing retail store customers at VAV (San Marcos Tanger Outlets).

## Features

- **Quick Mode**: Type a free-text description, Claude AI parses it into structured data
- **Detailed Mode**: Step-by-step inline keyboard entry (age, ethnicity, items, purchase, etc.)
- **Daily Reports**: Customer count, sales rate, revenue, demographic breakdown
- **Weekly Trends**: Day-by-day visualization, ethnicity trends, category analysis
- **AI Analysis**: Deep insights powered by Claude — customer profiles, pricing, marketing recommendations

## Tech Stack

- Python 3.11 + python-telegram-bot
- Claude API (Anthropic) — text parsing + analytics
- Supabase — PostgreSQL database (free tier)
- Vercel — serverless hosting (free tier)

## Setup

### 1. Telegram Bot Token

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Choose a name: `VAV Customer Tracker`
4. Choose a username: `vav_tracker_bot` (must end in "bot")
5. Copy the token

### 2. Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key
3. Copy it

### 3. Supabase Database

1. Go to [supabase.com](https://supabase.com) and create a free project
2. Go to **SQL Editor** in the dashboard
3. Paste and run the contents of `scripts/setup_supabase.sql`
4. Go to **Settings > API** and copy the **Project URL** and **anon/public key**

### 4. Environment Variables

```bash
cp .env.example .env
```

Fill in your `.env`:
```
TELEGRAM_BOT_TOKEN=your-token
ANTHROPIC_API_KEY=your-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 5. Deploy to Vercel

1. Push this project to GitHub
2. Go to [vercel.com/new](https://vercel.com/new) and import the repo
3. Add all 4 environment variables in Vercel dashboard (Settings > Environment Variables)
4. Deploy

### 6. Set Webhook

```bash
pip install -r requirements.txt
python scripts/set_webhook.py https://your-project.vercel.app
```

### 7. Test

Open Telegram, find your bot, send `/start`

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/yeni` | Detailed entry with buttons |
| `/bugun` | Today's summary report |
| `/hafta` | Weekly trend report |
| `/analiz` | AI-powered deep analysis |
| `/son` | Show last 5 entries |
| `/sil` | Delete last entry |
| `/help` | Help message |

**Quick mode**: Just type a customer description without any command!

## Cost

- Vercel: Free
- Supabase: Free
- Claude API: ~$2-5/month
