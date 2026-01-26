from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.constants import (
    MENU_INFO,
    MENU_COMPARE,
    MENU_QUIZ,
    MENU_STATS,
    MENU_FEEDBACK,
    MENU_BACK,
)


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU_INFO), KeyboardButton(text=MENU_COMPARE)],
            [KeyboardButton(text=MENU_QUIZ), KeyboardButton(text=MENU_STATS)],
            [KeyboardButton(text=MENU_FEEDBACK)],
        ],
        resize_keyboard=True,
    )


def back_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=MENU_BACK)]],
        resize_keyboard=True,
    )
