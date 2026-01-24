from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.constants import MODE_LABELS


def mode_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=MODE_LABELS["easy"], callback_data="mode:easy"),
            InlineKeyboardButton(text=MODE_LABELS["medium"], callback_data="mode:medium"),
        ],
        [
            InlineKeyboardButton(text=MODE_LABELS["hard"], callback_data="mode:hard"),
            InlineKeyboardButton(text=MODE_LABELS["mixed"], callback_data="mode:mixed"),
        ],
        [InlineKeyboardButton(text="⬅️ Мәзірге қайту", callback_data="menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def question_keyboard(question: dict, index: int, selected: Optional[set] = None) -> InlineKeyboardMarkup:
    selected = selected or set()
    options = question.get("options", {})
    correct = question.get("correct", [])
    is_multi = question.get("multi", False) or len(correct) > 1

    buttons = []
    for key in sorted(options.keys()):
        label = options[key]
        if is_multi:
            prefix = "✅" if key in selected else "☑️"
            text = f"{prefix} {key}) {label}"
            callback = f"toggle:{index}:{key}"
        else:
            text = f"{key}) {label}"
            callback = f"ans:{index}:{key}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback)])

    if is_multi:
        buttons.append(
            [InlineKeyboardButton(text="Жауапты бекіту", callback_data=f"submit:{index}")]
        )

    buttons.append([InlineKeyboardButton(text="⬅️ Мәзірге қайту", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
