from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.constants import MODE_LABELS


def compare_mode_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=MODE_LABELS["easy"], callback_data="cmpmode:easy"),
            InlineKeyboardButton(text=MODE_LABELS["medium"], callback_data="cmpmode:medium"),
        ],
        [
            InlineKeyboardButton(text=MODE_LABELS["hard"], callback_data="cmpmode:hard"),
            InlineKeyboardButton(text=MODE_LABELS["mixed"], callback_data="cmpmode:mixed"),
        ],
        [InlineKeyboardButton(text="⬅️ Мәзірге қайту", callback_data="menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def compare_question_keyboard(
    question: dict, index: int, selected: Optional[set] = None
) -> InlineKeyboardMarkup:
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
            callback = f"cmp:toggle:{index}:{key}"
        else:
            text = f"{key}) {label}"
            callback = f"cmp:ans:{index}:{key}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback)])

    if is_multi:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Жауапты бекіту",
                    callback_data=f"cmp:submit:{index}",
                )
            ]
        )

    buttons.append(
        [InlineKeyboardButton(text="⬅️ Мәзірге қайту", callback_data="menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
