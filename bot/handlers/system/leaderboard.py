from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.constants import MENU_LEADERBOARD
from bot.keyboards.system.menu import main_menu_keyboard
from bot.utils.loader import load_stats

router = Router()

TOP_LIMIT = 10


def _format_user_name(user_id: str, stats: dict) -> str:
    display_name = stats.get("display_name") or ""
    if display_name:
        return display_name
    username = stats.get("username") or ""
    if username:
        return f"@{username}"
    first_name = stats.get("first_name") or ""
    last_name = stats.get("last_name") or ""
    combined = " ".join(part for part in [first_name, last_name] if part)
    if combined:
        return combined
    return f"ID {user_id}"


def _format_leaderboard(stats: dict, current_user_id: str) -> str:
    entries = []
    for user_id, user_stats in stats.items():
        total_points = user_stats.get("total_points", 0)
        total_correct = user_stats.get("total_correct", 0)
        quizzes_taken = user_stats.get("quizzes_taken", 0)
        entries.append((user_id, total_points, total_correct, quizzes_taken, user_stats))

    if not entries:
        return "Әзірге лидерборд бос. Алдымен викторинадан өтіп көріңіз!"

    entries.sort(key=lambda item: (item[1], item[2], item[3]), reverse=True)
    top = entries[:TOP_LIMIT]

    lines = ["🏆 Лидерборд (ұпай бойынша):"]
    for index, (user_id, points, _correct, quizzes, user_stats) in enumerate(top, start=1):
        name = _format_user_name(user_id, user_stats)
        lines.append(f"{index}. {name} — {points} ұпай ({quizzes} викт.)")

    current_rank = None
    for index, (user_id, points, _correct, _quizzes, _user_stats) in enumerate(entries, start=1):
        if user_id == current_user_id:
            current_rank = (index, points)
            break

    if current_rank and current_rank[0] > TOP_LIMIT:
        lines.append("")
        lines.append(f"Сіздің орныңыз: {current_rank[0]} • {current_rank[1]} ұпай")

    return "\n".join(lines)


@router.message(Command("leaderboard"))
@router.message(F.text == MENU_LEADERBOARD)
async def leaderboard(message: Message) -> None:
    stats = load_stats()
    text = _format_leaderboard(stats, str(message.from_user.id))
    await message.answer(text, reply_markup=main_menu_keyboard())
