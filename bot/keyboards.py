"""Inline keyboard definitions for detailed customer entry mode."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Conversation states
(
    STATE_AGE,
    STATE_ETHNICITY,
    STATE_GROUP,
    STATE_LOOKED_AT,
    STATE_TRIED,
    STATE_PURCHASED,
    STATE_PRICE_SEGMENT,
    STATE_AMOUNT,
    STATE_PRICE_REACTION,
    STATE_MOOD,
    STATE_NOTES,
) = range(11)


def age_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("18-25", callback_data="age:18-25"),
            InlineKeyboardButton("25-35", callback_data="age:25-35"),
            InlineKeyboardButton("35-45", callback_data="age:35-45"),
        ],
        [
            InlineKeyboardButton("45-55", callback_data="age:45-55"),
            InlineKeyboardButton("55+", callback_data="age:55+"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def ethnicity_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("Hispanic/Latina", callback_data="eth:hispanic"),
            InlineKeyboardButton("White", callback_data="eth:white"),
        ],
        [
            InlineKeyboardButton("Black", callback_data="eth:black"),
            InlineKeyboardButton("Asian", callback_data="eth:asian"),
        ],
        [
            InlineKeyboardButton("Middle Eastern", callback_data="eth:middle_eastern"),
            InlineKeyboardButton("Mixed/Other", callback_data="eth:mixed_other"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def group_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("Tek", callback_data="grp:tek"),
            InlineKeyboardButton("2 kisi", callback_data="grp:2_kisi"),
            InlineKeyboardButton("Grup 3+", callback_data="grp:grup"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def looked_at_keyboard(selected: list[str] | None = None) -> InlineKeyboardMarkup:
    """Generate looked_at keyboard with checkmarks for selected items."""
    selected = selected or []
    items = [
        ("Elbise", "elbise"),
        ("Bluz", "bluz"),
        ("Pantolon", "pantolon"),
        ("Canta", "canta"),
        ("Sapka", "sapka"),
        ("Aksesuar", "aksesuar"),
    ]
    buttons = []
    row = []
    for label, value in items:
        check = "✅ " if value in selected else ""
        row.append(
            InlineKeyboardButton(
                f"{check}{label}", callback_data=f"look:{value}"
            )
        )
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append(
        [InlineKeyboardButton("✅ Devam →", callback_data="look:done")]
    )
    return InlineKeyboardMarkup(buttons)


def tried_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("Evet", callback_data="tried:yes"),
            InlineKeyboardButton("Hayir", callback_data="tried:no"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def purchased_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("✅ Evet, aldi", callback_data="purch:yes"),
            InlineKeyboardButton("❌ Hayir, almadi", callback_data="purch:no"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def price_segment_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("Indirimli", callback_data="seg:indirimli"),
            InlineKeyboardButton("Normal", callback_data="seg:normal"),
        ],
        [
            InlineKeyboardButton("Premium", callback_data="seg:premium"),
            InlineKeyboardButton("Karisik", callback_data="seg:karisik"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def amount_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("$1-25", callback_data="amt:$1-25"),
            InlineKeyboardButton("$25-50", callback_data="amt:$25-50"),
        ],
        [
            InlineKeyboardButton("$50-100", callback_data="amt:$50-100"),
            InlineKeyboardButton("$100-200", callback_data="amt:$100-200"),
        ],
        [
            InlineKeyboardButton("$200+", callback_data="amt:$200+"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def price_reaction_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("Sormadi", callback_data="pr:sormadi"),
            InlineKeyboardButton("Normal buldu", callback_data="pr:normal"),
        ],
        [
            InlineKeyboardButton("Pahali buldu", callback_data="pr:pahali"),
            InlineKeyboardButton("Pazarlik istedi", callback_data="pr:pazarlik"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def mood_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("😊 Memnun", callback_data="mood:memnun"),
            InlineKeyboardButton("😐 Kararsiz", callback_data="mood:kararsiz"),
            InlineKeyboardButton("😞 Mutsuz", callback_data="mood:mutsuz"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def skip_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("⏭️ Gec", callback_data="notes:skip")],
    ]
    return InlineKeyboardMarkup(buttons)


def confirm_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("✅ Dogru", callback_data="confirm:yes"),
            InlineKeyboardButton("✏️ Duzelt", callback_data="confirm:edit"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)
