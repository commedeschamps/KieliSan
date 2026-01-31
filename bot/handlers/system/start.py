from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.constants import WELCOME_TEXT, HELP_TEXT, ABOUT_TEXT, MENU_BACK, MENU_HELP, MENU_ABOUT
from bot.keyboards.system.menu import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(F.text == MENU_HELP)
async def menu_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(F.text == MENU_ABOUT)
async def menu_about(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(ABOUT_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Мәзірге оралдық.", reply_markup=main_menu_keyboard())


@router.message(lambda msg: msg.text == MENU_BACK)
async def menu_back(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Мәзірге оралдық.", reply_markup=main_menu_keyboard())
