import random
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, User
from aiogram.fsm.context import FSMContext

from bot.constants import (
    MENU_QUIZ,
    MENU_BACK,
    MODE_TO_LEVEL,
    MODE_LABELS,
    POINTS_BY_LEVEL,
    POINTS_DEFAULT,
)
from bot.keyboards.system.menu import main_menu_keyboard, back_menu_keyboard
from bot.keyboards.quiz.quiz import mode_keyboard, question_keyboard
from bot.states.quiz import QuizStates
from bot.utils.loader import load_questions, load_stats, save_stats

router = Router()


def _is_multi(question: dict) -> bool:
    return question.get("multi", False) or len(question.get("correct", [])) > 1


def _format_question_text(question: dict, index: int, total: int) -> str:
    title = question.get("title", "")
    level = question.get("level", "")
    question_text = question.get("question", "")
    options = question.get("options", {})

    lines = []
    if title:
        lines.append(f"<b>{title}</b>")
    lines.append(f"Сұрақ {index + 1}/{total} • Деңгей: {level}")
    lines.append("")
    lines.append(question_text)
    lines.append("")
    for key in sorted(options.keys()):
        lines.append(f"{key}) {options[key]}")
    if _is_multi(question):
        lines.append("")
        lines.append("Бірнеше дұрыс жауап болуы мүмкін.")
    return "\n".join(lines)


def _select_questions(mode: str) -> list[dict]:
    questions = load_questions()
    if mode == "mixed":
        random.shuffle(questions)
        return questions
    level = MODE_TO_LEVEL.get(mode)
    filtered = [q for q in questions if q.get("level") == level]
    random.shuffle(filtered)
    return filtered


def _build_explanation(question: dict, is_correct: bool) -> str:
    prefix = "✅ Дұрыс!" if is_correct else "❌ Қате."
    correct = ", ".join(question.get("correct", []))
    explanation = question.get("explanation", "")
    return f"{prefix}\nДұрыс жауап: {correct}\n{explanation}"


def _points_for_question(question: dict) -> int:
    level = question.get("level", "")
    return POINTS_BY_LEVEL.get(level, POINTS_DEFAULT)


def _format_user_label(user: User) -> str:
    if user.username:
        return f"@{user.username}"
    parts = [user.first_name, user.last_name]
    label = " ".join([part for part in parts if part])
    return label or f"ID {user.id}"


def _update_user_stats(user: User, correct: int, total: int, mode: str, points: int) -> None:
    stats = load_stats()
    key = str(user.id)
    user_stats = stats.get(
        key,
        {
            "quizzes_taken": 0,
            "total_correct": 0,
            "total_questions": 0,
            "best_score": 0,
            "best_total": 0,
            "last_score": 0,
            "last_total": 0,
            "last_mode": "-",
            "last_date": "-",
            "total_points": 0,
            "last_points": 0,
            "best_points": 0,
            "display_name": "",
            "username": "",
            "first_name": "",
            "last_name": "",
        },
    )

    user_stats.setdefault("total_points", 0)
    user_stats.setdefault("last_points", 0)
    user_stats.setdefault("best_points", 0)
    user_stats.setdefault("display_name", "")
    user_stats.setdefault("username", "")
    user_stats.setdefault("first_name", "")
    user_stats.setdefault("last_name", "")

    user_stats["quizzes_taken"] += 1
    user_stats["total_correct"] += correct
    user_stats["total_questions"] += total
    user_stats["last_score"] = correct
    user_stats["last_total"] = total
    user_stats["last_mode"] = MODE_LABELS.get(mode, mode)
    user_stats["last_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    user_stats["total_points"] += points
    user_stats["last_points"] = points
    if points > user_stats.get("best_points", 0):
        user_stats["best_points"] = points

    user_stats["display_name"] = _format_user_label(user)
    user_stats["username"] = user.username or ""
    user_stats["first_name"] = user.first_name or ""
    user_stats["last_name"] = user.last_name or ""

    best_total = user_stats.get("best_total", 0)
    best_score = user_stats.get("best_score", 0)
    best_ratio = (best_score / best_total) if best_total else 0
    current_ratio = (correct / total) if total else 0
    if current_ratio > best_ratio:
        user_stats["best_score"] = correct
        user_stats["best_total"] = total

    stats[key] = user_stats
    save_stats(stats)


async def _send_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    questions = data.get("questions", [])
    index = data.get("current_index", 0)

    if index >= len(questions):
        return

    question = questions[index]
    selected = set(data.get("selected", []))
    text = _format_question_text(question, index, len(questions))
    await message.answer(
        text,
        reply_markup=question_keyboard(question, index, selected),
    )


async def _finish_quiz(message: Message, state: FSMContext, user: User) -> None:
    data = await state.get_data()
    correct = data.get("correct_count", 0)
    total = len(data.get("questions", []))
    mode = data.get("mode", "mixed")
    points = data.get("points", 0)

    _update_user_stats(user, correct, total, mode, points)
    await state.clear()

    await message.answer(
        f"Викторина аяқталды!\nНәтиже: {correct}/{total} дұрыс жауап бердіңіз.\nҰпай: {points}",
        reply_markup=main_menu_keyboard(),
    )


@router.message(F.text == MENU_QUIZ)
async def quiz_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Деңгейді таңдаңыз:",
        reply_markup=mode_keyboard(),
    )


@router.callback_query(F.data.startswith("mode:"))
async def quiz_start(callback: CallbackQuery, state: FSMContext) -> None:
    mode = callback.data.split(":", 1)[1]
    questions = _select_questions(mode)
    if not questions:
        await callback.message.answer(
            "Бұл деңгейде сұрақтар табылмады. Басқа деңгейді таңдаңыз.",
            reply_markup=mode_keyboard(),
        )
        await callback.answer()
        return

    await state.set_state(QuizStates.in_quiz)
    await state.update_data(
        mode=mode,
        questions=questions,
        current_index=0,
        correct_count=0,
        points=0,
        selected=[],
    )

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await callback.message.answer(
        f"Викторина басталды! Сұрақ саны: {len(questions)}.",
        reply_markup=back_menu_keyboard(),
    )
    await _send_question(callback.message, state)
    await callback.answer()


@router.callback_query(QuizStates.in_quiz, F.data.startswith("ans:"))
async def quiz_answer(callback: CallbackQuery, state: FSMContext) -> None:
    _, index_str, choice = callback.data.split(":")
    data = await state.get_data()
    current_index = data.get("current_index", 0)

    if int(index_str) != current_index:
        await callback.answer("Бұл сұрақтың жауабы қабылданды.", show_alert=False)
        return

    questions = data.get("questions", [])
    question = questions[current_index]
    correct_set = set(question.get("correct", []))
    is_correct = {choice} == correct_set
    if is_correct:
        await state.update_data(
            correct_count=data.get("correct_count", 0) + 1,
            points=data.get("points", 0) + _points_for_question(question),
        )

    await callback.message.answer(_build_explanation(question, is_correct))

    next_index = current_index + 1
    if next_index >= len(questions):
        await _finish_quiz(callback.message, state, callback.from_user)
    else:
        await state.update_data(current_index=next_index, selected=[])
        await _send_question(callback.message, state)
    await callback.answer()


@router.callback_query(QuizStates.in_quiz, F.data.startswith("toggle:"))
async def quiz_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    _, index_str, choice = callback.data.split(":")
    data = await state.get_data()
    current_index = data.get("current_index", 0)

    if int(index_str) != current_index:
        await callback.answer("Бұл сұрақ өзекті емес.", show_alert=False)
        return

    selected = set(data.get("selected", []))
    if choice in selected:
        selected.remove(choice)
    else:
        selected.add(choice)

    await state.update_data(selected=list(selected))

    question = data.get("questions", [])[current_index]
    await callback.message.edit_reply_markup(
        reply_markup=question_keyboard(question, current_index, selected)
    )
    await callback.answer()


@router.callback_query(QuizStates.in_quiz, F.data.startswith("submit:"))
async def quiz_submit(callback: CallbackQuery, state: FSMContext) -> None:
    _, index_str = callback.data.split(":")
    data = await state.get_data()
    current_index = data.get("current_index", 0)

    if int(index_str) != current_index:
        await callback.answer("Бұл сұрақ өзекті емес.", show_alert=False)
        return

    selected = set(data.get("selected", []))
    if not selected:
        await callback.answer("Кемінде бір нұсқа таңдаңыз.", show_alert=True)
        return

    question = data.get("questions", [])[current_index]
    correct_set = set(question.get("correct", []))
    is_correct = selected == correct_set
    if is_correct:
        await state.update_data(
            correct_count=data.get("correct_count", 0) + 1,
            points=data.get("points", 0) + _points_for_question(question),
        )

    await callback.message.answer(_build_explanation(question, is_correct))

    next_index = current_index + 1
    if next_index >= len(data.get("questions", [])):
        await _finish_quiz(callback.message, state, callback.from_user)
    else:
        await state.update_data(current_index=next_index, selected=[])
        await _send_question(callback.message, state)
    await callback.answer()


@router.message(QuizStates.in_quiz, F.text == MENU_BACK)
async def quiz_back_text(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Мәзірге оралдық.", reply_markup=main_menu_keyboard())


@router.message(QuizStates.in_quiz, F.text != MENU_BACK)
async def quiz_text_fallback(message: Message) -> None:
    await message.answer("Жауапты төмендегі батырмалар арқылы таңдаңыз.")
