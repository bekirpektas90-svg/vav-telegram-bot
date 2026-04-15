"""Telegram bot command and message handlers for VAV Customer Tracker."""

from telegram import Bot, Update
from telegram.constants import ChatAction, ParseMode

from bot import keyboards as kb
from bot import messages as msg
from services import database as db
from services.claude_parser import parse_customer_text, format_parsed_result
from services.claude_analyzer import (
    generate_daily_report,
    generate_weekly_report,
    generate_ai_analysis,
)
from services.claude_chat import get_chat_response, clear_chat_history

# In-memory state for detailed entry mode (per user)
# Key: chat_id, Value: {"state": int, "data": dict}
user_sessions: dict[int, dict] = {}

# Track which users are in AI chat mode
ai_mode_users: set[int] = set()


async def handle_update(bot: Bot, update: Update):
    """Route incoming updates to appropriate handlers."""
    # Handle callback queries (inline keyboard button presses)
    if update.callback_query:
        await handle_callback(bot, update)
        return

    if not update.message or not update.message.text:
        return

    chat_id = update.message.chat_id
    text = update.message.text.strip()
    username = update.message.from_user.first_name or update.message.from_user.username or "?"

    if text == "/start":
        await bot.send_message(chat_id=chat_id, text=msg.WELCOME)
    elif text == "/help":
        await bot.send_message(chat_id=chat_id, text=msg.HELP)
    elif text == "/ai":
        await handle_ai_mode_on(bot, chat_id)
    elif text == "/musteri":
        await handle_ai_mode_off(bot, chat_id)
    elif text == "/yeni":
        ai_mode_users.discard(chat_id)
        await handle_new_entry(bot, chat_id)
    elif text == "/bugun":
        await handle_today_report(bot, chat_id)
    elif text == "/hafta":
        await handle_week_report(bot, chat_id)
    elif text == "/analiz":
        await handle_ai_analysis(bot, chat_id)
    elif text == "/son":
        await handle_last_entries(bot, chat_id)
    elif text == "/sil":
        await handle_delete_last(bot, chat_id, username)
    elif text.startswith("?"):
        # Single AI question without switching modes
        question = text[1:].strip()
        if question:
            await handle_ai_chat(bot, chat_id, question)
    else:
        # Check if user is in notes state of detailed mode
        session = user_sessions.get(chat_id)
        if session and session["state"] == kb.STATE_NOTES:
            await handle_notes_text(bot, chat_id, text, username)
        elif chat_id in ai_mode_users:
            # AI chat mode
            await handle_ai_chat(bot, chat_id, text)
        else:
            # Quick mode: free text customer entry
            await handle_quick_entry(bot, chat_id, text, username)


# --- AI Chat Mode ---

async def handle_ai_mode_on(bot: Bot, chat_id: int):
    """Enable AI chat mode."""
    ai_mode_users.add(chat_id)
    await bot.send_message(
        chat_id=chat_id,
        text="🤖 AI modu acildi! Benimle her konuda konusabilirsin.\n\n"
             "Musteri kaydi yapmak icin /musteri yaz veya /yeni ile detayli gir.\n"
             "Tek seferlik soru icin ? ile basla (ornek: ?bugun nasil satis yapabilirim)",
    )


async def handle_ai_mode_off(bot: Bot, chat_id: int):
    """Disable AI chat mode, return to customer tracking."""
    ai_mode_users.discard(chat_id)
    clear_chat_history(chat_id)
    await bot.send_message(
        chat_id=chat_id,
        text="📋 Musteri kayit moduna donuldu. Artik yazdigin mesajlar musteri kaydi olarak islenir.\n\n"
             "AI ile konusmak icin /ai yaz.",
    )


async def handle_ai_chat(bot: Bot, chat_id: int, text: str):
    """Handle AI chat message."""
    try:
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception:
        pass

    response = get_chat_response(chat_id, text)

    # Telegram message limit
    try:
        if len(response) > 4000:
            parts = [response[i : i + 4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await bot.send_message(chat_id=chat_id, text=part)
        else:
            await bot.send_message(chat_id=chat_id, text=response)
    except Exception as e:
        print(f"AI chat send error: {e}")


# --- Quick Mode ---

async def handle_quick_entry(bot: Bot, chat_id: int, text: str, username: str):
    """Parse free-text message and save as customer record."""
    try:
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception:
        pass  # Ignore typing indicator errors

    parsed = parse_customer_text(text)
    if not parsed:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="❌ Mesaji anlayamadim. Ornek:\n\"30lu hispanic kadin, elbise denedi, almadi\"",
            )
        except Exception:
            pass
        return

    # Save to database first (before sending response)
    record = {
        "recorded_by": username,
        "input_mode": "quick",
        "raw_message": text,
        **parsed,
    }
    try:
        db.insert_customer(record)
    except Exception as e:
        print(f"DB insert error: {e}")
        try:
            await bot.send_message(chat_id=chat_id, text=msg.ERROR_MESSAGE)
        except Exception:
            pass
        return

    # Show formatted result with confirm keyboard
    result_text = format_parsed_result(parsed)
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=result_text,
            reply_markup=kb.confirm_keyboard(),
        )
    except Exception as e:
        print(f"Telegram send error (record saved): {e}")


# --- Detailed Mode ---

async def handle_new_entry(bot: Bot, chat_id: int):
    """Start a new detailed customer entry."""
    user_sessions[chat_id] = {
        "state": kb.STATE_AGE,
        "data": {},
    }
    await bot.send_message(
        chat_id=chat_id,
        text=msg.AGE_QUESTION,
        reply_markup=kb.age_keyboard(),
    )


async def handle_callback(bot: Bot, update: Update):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    chat_id = query.message.chat_id
    data = query.data
    username = query.from_user.first_name or query.from_user.username or "?"

    # Acknowledge the callback
    await query.answer()

    # Confirm/edit callbacks (from quick mode)
    if data == "confirm:yes":
        await query.edit_message_reply_markup(reply_markup=None)
        return
    if data == "confirm:edit":
        await query.edit_message_text("✏️ Yeniden yaz veya /yeni ile detayli gir.")
        return

    # Detailed mode callbacks
    session = user_sessions.get(chat_id)
    if not session:
        await bot.send_message(chat_id=chat_id, text="⚠️ Aktif giris yok. /yeni ile basla.")
        return

    state = session["state"]
    customer = session["data"]

    if state == kb.STATE_AGE and data.startswith("age:"):
        customer["age_range"] = data.split(":")[1]
        session["state"] = kb.STATE_ETHNICITY
        await query.edit_message_text(
            msg.ETHNICITY_QUESTION, reply_markup=kb.ethnicity_keyboard()
        )

    elif state == kb.STATE_ETHNICITY and data.startswith("eth:"):
        customer["ethnicity"] = data.split(":")[1]
        session["state"] = kb.STATE_GROUP
        await query.edit_message_text(
            msg.GROUP_QUESTION, reply_markup=kb.group_keyboard()
        )

    elif state == kb.STATE_GROUP and data.startswith("grp:"):
        customer["group_size"] = data.split(":")[1]
        session["state"] = kb.STATE_LOOKED_AT
        customer["looked_at"] = []
        await query.edit_message_text(
            msg.LOOKED_AT_QUESTION, reply_markup=kb.looked_at_keyboard([])
        )

    elif state == kb.STATE_LOOKED_AT and data.startswith("look:"):
        value = data.split(":")[1]
        if value == "done":
            session["state"] = kb.STATE_TRIED
            await query.edit_message_text(
                msg.TRIED_QUESTION, reply_markup=kb.tried_keyboard()
            )
        else:
            # Toggle selection
            looked = customer.get("looked_at", [])
            if value in looked:
                looked.remove(value)
            else:
                looked.append(value)
            customer["looked_at"] = looked
            await query.edit_message_reply_markup(
                reply_markup=kb.looked_at_keyboard(looked)
            )

    elif state == kb.STATE_TRIED and data.startswith("tried:"):
        customer["tried_on"] = data.split(":")[1] == "yes"
        if customer["tried_on"]:
            customer["tried_count"] = 1  # Default
        session["state"] = kb.STATE_PURCHASED
        await query.edit_message_text(
            msg.PURCHASED_QUESTION, reply_markup=kb.purchased_keyboard()
        )

    elif state == kb.STATE_PURCHASED and data.startswith("purch:"):
        purchased = data.split(":")[1] == "yes"
        customer["purchased"] = purchased
        if purchased:
            session["state"] = kb.STATE_PRICE_SEGMENT
            await query.edit_message_text(
                msg.PRICE_SEGMENT_QUESTION, reply_markup=kb.price_segment_keyboard()
            )
        else:
            session["state"] = kb.STATE_PRICE_REACTION
            await query.edit_message_text(
                msg.PRICE_REACTION_QUESTION, reply_markup=kb.price_reaction_keyboard()
            )

    elif state == kb.STATE_PRICE_SEGMENT and data.startswith("seg:"):
        customer["price_segment"] = data.split(":")[1]
        session["state"] = kb.STATE_AMOUNT
        await query.edit_message_text(
            msg.AMOUNT_QUESTION, reply_markup=kb.amount_keyboard()
        )

    elif state == kb.STATE_AMOUNT and data.startswith("amt:"):
        customer["amount_range"] = data.split(":")[1]
        session["state"] = kb.STATE_MOOD
        await query.edit_message_text(
            msg.MOOD_QUESTION, reply_markup=kb.mood_keyboard()
        )

    elif state == kb.STATE_PRICE_REACTION and data.startswith("pr:"):
        customer["price_reaction"] = data.split(":")[1]
        session["state"] = kb.STATE_MOOD
        await query.edit_message_text(
            msg.MOOD_QUESTION, reply_markup=kb.mood_keyboard()
        )

    elif state == kb.STATE_MOOD and data.startswith("mood:"):
        customer["mood"] = data.split(":")[1]
        session["state"] = kb.STATE_NOTES
        await query.edit_message_text(
            msg.NOTES_QUESTION, reply_markup=kb.skip_keyboard()
        )

    elif state == kb.STATE_NOTES and data == "notes:skip":
        # Save without notes
        await save_detailed_entry(bot, chat_id, username, query)


async def handle_notes_text(bot: Bot, chat_id: int, text: str, username: str):
    """Handle free-text notes in detailed mode."""
    session = user_sessions.get(chat_id)
    if not session:
        return
    session["data"]["notes"] = text
    await save_detailed_entry(bot, chat_id, username)


async def save_detailed_entry(bot: Bot, chat_id: int, username: str, query=None):
    """Save the completed detailed entry to database."""
    session = user_sessions.get(chat_id)
    if not session:
        return

    customer = session["data"]
    record = {
        "recorded_by": username,
        "input_mode": "detailed",
        **customer,
    }

    try:
        db.insert_customer(record)
    except Exception as e:
        print(f"DB insert error: {e}")
        await bot.send_message(chat_id=chat_id, text=msg.ERROR_MESSAGE)
        del user_sessions[chat_id]
        return

    # Format summary
    result_text = format_parsed_result(customer)
    if query:
        await query.edit_message_text(result_text)
    else:
        await bot.send_message(chat_id=chat_id, text=result_text)

    # Get today's count
    today = db.get_today_customers()
    await bot.send_message(
        chat_id=chat_id,
        text=f"📊 Bugun toplam: {len(today)} musteri",
    )

    del user_sessions[chat_id]


# --- Reports ---

async def handle_today_report(bot: Bot, chat_id: int):
    """Generate and send daily report."""
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.send_message(chat_id=chat_id, text=msg.GENERATING_REPORT)

    customers = db.get_today_customers()
    report = generate_daily_report(customers)
    await bot.send_message(chat_id=chat_id, text=report)


async def handle_week_report(bot: Bot, chat_id: int):
    """Generate and send weekly report."""
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.send_message(chat_id=chat_id, text=msg.GENERATING_REPORT)

    customers = db.get_week_customers()
    report = generate_weekly_report(customers)
    await bot.send_message(chat_id=chat_id, text=report)


async def handle_ai_analysis(bot: Bot, chat_id: int):
    """Generate and send AI-powered deep analysis."""
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await bot.send_message(chat_id=chat_id, text=msg.ANALYZING)

    customers = db.get_all_customers_for_analysis()
    report = generate_ai_analysis(customers)

    # Telegram message limit is 4096 chars
    if len(report) > 4000:
        parts = [report[i : i + 4000] for i in range(0, len(report), 4000)]
        for part in parts:
            await bot.send_message(chat_id=chat_id, text=part)
    else:
        await bot.send_message(chat_id=chat_id, text=report)


# --- Utility ---

async def handle_last_entries(bot: Bot, chat_id: int):
    """Show the last 5 customer entries."""
    records = db.get_last_n_customers(5)
    if not records:
        await bot.send_message(chat_id=chat_id, text=msg.NO_RECORDS)
        return

    lines = ["📋 Son 5 musteri kaydi:\n"]
    for i, r in enumerate(records, 1):
        parts = [f"{i}."]
        if r.get("age_range"):
            parts.append(r["age_range"])
        if r.get("ethnicity"):
            parts.append(r["ethnicity"].capitalize())
        if r.get("group_size"):
            grp = {"tek": "Tek", "2_kisi": "2 kisi", "grup": "Grup"}.get(
                r["group_size"], r["group_size"]
            )
            parts.append(grp)
        if r.get("purchased"):
            amt = r.get("exact_amount") or r.get("amount_range") or ""
            parts.append(f"💰 ${amt}" if amt else "💰 Aldi")
        else:
            parts.append("❌")
        if r.get("recorded_by"):
            parts.append(f"({r['recorded_by']})")
        if r.get("recorded_at"):
            time_str = r["recorded_at"][11:16]  # HH:MM
            parts.append(time_str)
        lines.append(" | ".join(parts))

    await bot.send_message(chat_id=chat_id, text="\n".join(lines))


async def handle_delete_last(bot: Bot, chat_id: int, username: str):
    """Delete the last customer entry by this user."""
    deleted = db.delete_last_customer(username)
    if deleted:
        await bot.send_message(chat_id=chat_id, text=msg.RECORD_DELETED)
    else:
        await bot.send_message(chat_id=chat_id, text=msg.NO_RECORD_TO_DELETE)
