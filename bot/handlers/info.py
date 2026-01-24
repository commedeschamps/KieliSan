from aiogram import Router, F
from aiogram.types import Message

from bot.constants import MENU_INFO, INFO_TEXT
from bot.keyboards.menu import main_menu_keyboard

router = Router()


@router.message(F.text == MENU_INFO)
async def info(message: Message) -> None:
    await message.answer(INFO_TEXT, reply_markup=main_menu_keyboard())
