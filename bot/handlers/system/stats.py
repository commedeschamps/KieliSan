from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.constants import MENU_STATS
from bot.keyboards.system.menu import main_menu_keyboard
from bot.utils.loader import load_stats

router = Router()


def _format_stats(user_stats: dict) -> str:
    quizzes_taken = user_stats.get("quizzes_taken", 0)
    total_correct = user_stats.get("total_correct", 0)
    total_questions = user_stats.get("total_questions", 0)
    last_score = user_stats.get("last_score", 0)
    last_total = user_stats.get("last_total", 0)
    last_mode = user_stats.get("last_mode", "-")
    last_date = user_stats.get("last_date", "-")
    best_score = user_stats.get("best_score", 0)
    best_total = user_stats.get("best_total", 0)
    total_points = user_stats.get("total_points", 0)
    last_points = user_stats.get("last_points", 0)
    best_points = user_stats.get("best_points", 0)

    avg_pct = 0
    if total_questions:
        avg_pct = round((total_correct / total_questions) * 100)

    return (
        "📊 Сіздің статистикаңыз:\n"
        f"• Викторина саны: {quizzes_taken}\n"
        f"• Орташа нәтиже: {avg_pct}%\n"
        f"• Жалпы ұпай: {total_points}\n"
        f"• Ең жоғары ұпай: {best_points}\n"
        f"• Ең жақсы нәтиже: {best_score}/{best_total}\n"
        f"• Соңғы нәтиже: {last_score}/{last_total} ({last_mode})\n"
        f"• Соңғы ұпай: {last_points}\n"
        f"• Соңғы өту уақыты: {last_date}"
    )


@router.message(Command("stats"))
@router.message(F.text == MENU_STATS)
async def stats(message: Message) -> None:
    stats_data = load_stats()
    user_stats = stats_data.get(str(message.from_user.id))
    if not user_stats:
        await message.answer(
            "Әзірге статистика жоқ. Алдымен викторинадан өтіп көріңіз!",
            reply_markup=main_menu_keyboard(),
        )
        return

    await message.answer(_format_stats(user_stats), reply_markup=main_menu_keyboard())
