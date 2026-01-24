from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.constants import MENU_FEEDBACK, MENU_BACK
from bot.keyboards.menu import main_menu_keyboard, back_menu_keyboard
from bot.states.quiz import FeedbackStates
from bot.utils.loader import append_feedback

router = Router()


@router.message(F.text == MENU_FEEDBACK)
async def feedback_start(message: Message, state: FSMContext) -> None:
    await state.set_state(FeedbackStates.waiting)
    await message.answer(
        "Кері байланыс жазыңыз. Ұсыныс немесе пікіріңізді күтемін!",
        reply_markup=back_menu_keyboard(),
    )


@router.message(FeedbackStates.waiting)
async def feedback_receive(message: Message, state: FSMContext) -> None:
    if message.text == MENU_BACK:
        await state.clear()
        await message.answer("Мәзірге оралдық.", reply_markup=main_menu_keyboard())
        return

    entry = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "text": message.text or "",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    append_feedback(entry)

    await state.clear()
    await message.answer(
        "Рақмет! Пікіріңіз қабылданды ✅",
        reply_markup=main_menu_keyboard(),
    )
