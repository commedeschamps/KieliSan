from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.system.menu import main_menu_keyboard

router = Router()


@router.callback_query(F.data == "menu")
async def inline_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.message.answer("Мәзірге оралдық.", reply_markup=main_menu_keyboard())
    await callback.answer()
