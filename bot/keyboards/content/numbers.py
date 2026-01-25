from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def numbers_keyboard(numbers: list[str]) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for idx, num in enumerate(numbers, start=1):
        row.append(InlineKeyboardButton(text=num, callback_data=f"num:{num}"))
        if idx % 3 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([InlineKeyboardButton(text="🎲 Кездейсоқ сан көру", callback_data="num:random")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def number_info_keyboard(number: str, mode: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="Ақпарат: Қысқа / Толық",
                callback_data=f"num:toggle:{number}:{mode}",
            )
        ],
    ]

    rows.extend(
        [
            [InlineKeyboardButton(text="Келесі сан", callback_data="num:next")],
            [
                InlineKeyboardButton(text="⬅️ Сандар тізімі", callback_data="num:list"),
                InlineKeyboardButton(text="⬅️ Мәзір", callback_data="menu"),
            ],
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=rows)


def number_quiz_keyboard(number: str, options: dict) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for key in ["A", "B", "C", "D"]:
        if key in options:
            rows.append(
                [
                    InlineKeyboardButton(
                        text=key,
                        callback_data=f"num:ans:{number}:{key}",
                    )
                ]
            )
    return InlineKeyboardMarkup(inline_keyboard=rows)
