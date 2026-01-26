from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CULTURE_CODE_TO_LABEL = {
    "kazakh": "🇰🇿 Қазақ / Түркі",
    "islam": "☪️ Ислам",
    "christ": "✝️ Христиан",
    "persian": "🇮🇷 Парсы",
    "hindu": "🇮🇳 Үнді",
    "china": "🇨🇳 Қытай",
    "mongol": "🇲🇳 Моңғол",
    "summary": "🧭 Қысқаша салыстыру",
}
CULTURE_ORDER = [
    "kazakh",
    "islam",
    "christ",
    "persian",
    "hindu",
    "china",
    "mongol",
    "summary",
]


def compare_numbers_keyboard(numbers: list[str]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for idx, num in enumerate(numbers, start=1):
        row.append(InlineKeyboardButton(text=num, callback_data=f"cmp:num:{num}"))
        if idx % 3 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append(
        [InlineKeyboardButton(text="🧠 Салыстырмалы викторина", callback_data="cmp:quiz")]
    )
    rows.append([InlineKeyboardButton(text="⬅️ Мәзір", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _culture_rows(number: str) -> list[list[InlineKeyboardButton]]:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for code in CULTURE_ORDER:
        label = CULTURE_CODE_TO_LABEL.get(code, code)
        row.append(
            InlineKeyboardButton(text=label, callback_data=f"cmp:cul:{number}:{code}")
        )
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return rows


def compare_info_keyboard(number: str, view: str) -> InlineKeyboardMarkup:
    view_buttons = [
        InlineKeyboardButton(text="🌍 Салыстыру (қысқа)", callback_data=f"cmp:view:{number}:compare"),
        InlineKeyboardButton(text="📖 Толық барлық мәдениет", callback_data=f"cmp:view:{number}:full"),
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            *_culture_rows(number),
            view_buttons,
            [
                InlineKeyboardButton(text="⬅️ Сандар тізімі", callback_data="cmp:list"),
                InlineKeyboardButton(text="🧠 Салыстырмалы викторина", callback_data="cmp:quiz"),
            ],
            [InlineKeyboardButton(text="⬅️ Мәзір", callback_data="menu")],
        ]
    )
