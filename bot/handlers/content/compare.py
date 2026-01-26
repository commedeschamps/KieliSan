import random
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.constants import MENU_COMPARE, MENU_BACK, MODE_TO_LEVEL
from bot.keyboards.system.menu import main_menu_keyboard, back_menu_keyboard
from bot.keyboards.content.compare import compare_numbers_keyboard, compare_info_keyboard
from bot.keyboards.quiz.compare import compare_mode_keyboard, compare_question_keyboard
from bot.states.quiz import CompareQuizStates
from bot.utils.loader import load_compare_text, load_compare_questions

router = Router()

COMPARE_NUMBERS = ["3", "5", "7", "9", "40"]
CULTURE_CODE_TO_PLAIN = {
    "kazakh": "Қазақ / Түркі",
    "islam": "Ислам",
    "christ": "Христиан",
    "persian": "Парсы",
    "hindu": "Үнді",
    "china": "Қытай",
    "mongol": "Моңғол",
    "summary": "Қысқаша салыстыру",
}
CULTURE_KEYS = list(CULTURE_CODE_TO_PLAIN.values())


def _extract_section(text: str, number: str) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    start_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{number} саны"):
            start_idx = i
            break
    if start_idx is None:
        return ""

    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        for other in COMPARE_NUMBERS:
            if lines[j].strip().startswith(f"{other} саны"):
                end_idx = j
                break
        if end_idx != len(lines):
            break

    section = "\n".join(lines[start_idx:end_idx]).strip()
    for stop_marker in ("<hr>", "Қорытынды:"):
        if stop_marker in section:
            section = section.split(stop_marker, 1)[0].strip()
    return section


def _split_text(text: str, limit: int = 4000) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts: list[str] = []
    current = ""
    for block in text.split("\n\n"):
        candidate = f"{current}\n\n{block}" if current else block
        if len(candidate) <= limit:
            current = candidate
        else:
            if current:
                parts.append(current)
                current = block
            else:
                # Fallback hard split
                while len(block) > limit:
                    parts.append(block[:limit])
                    block = block[limit:]
                current = block
    if current:
        parts.append(current)
    return parts


def _format_section(section: str) -> str:
    if not section:
        return ""
    lines = [line for line in section.splitlines()]
    if lines:
        lines[0] = f"<b>{lines[0]}</b>"
    return "\n".join(lines)


def _match_culture(label: str) -> Optional[str]:
    for key in CULTURE_KEYS:
        if label.startswith(key):
            return key
    return None


def _parse_cultures(section: str) -> tuple[str, list[dict]]:
    lines = [line.rstrip() for line in section.splitlines()]
    if not lines:
        return "", []
    header = lines[0].strip()
    blocks: list[dict] = []
    current: Optional[dict] = None

    for line in lines[1:]:
        stripped = line.strip()
        if not stripped:
            if current and current["text"]:
                current["text"].append("")
            continue

        if ":" in stripped:
            label, rest = stripped.split(":", 1)
            key = _match_culture(label.strip())
            if key:
                if current:
                    current["text"] = "\n".join(current["text"]).strip()
                    blocks.append(current)
                current = {
                    "key": key,
                    "label": label.strip(),
                    "text": [rest.strip()],
                }
                continue

        if current:
            current["text"].append(stripped)

    if current:
        current["text"] = "\n".join(current["text"]).strip()
        blocks.append(current)

    return header, blocks


def _shorten_text(text: str, max_chars: int = 320) -> str:
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    for sep in [". ", "! ", "? ", "… "]:
        idx = cut.rfind(sep)
        if idx > 50:
            cut = cut[: idx + len(sep.strip())]
            break
    return cut.rstrip() + "..."


def _render_compare(section: str, view: str) -> str:
    if not section:
        return ""
    header, blocks = _parse_cultures(section)
    if not blocks:
        return _format_section(section)

    def find_block(key: str) -> Optional[dict]:
        for block in blocks:
            if block["key"] == key:
                return block
        return None

    def add_block(lines: list[str], block: dict, short: bool = False) -> None:
        text = block.get("text", "")
        if short:
            text = _shorten_text(text)
        lines.append(f"<b>{block.get('label', block.get('key', ''))}</b>")
        if text:
            lines.append(text)

    lines: list[str] = []
    if header:
        lines.append(f"<b>{header}</b>")

    kazakh = find_block("Қазақ / Түркі")
    summary = find_block("Қысқаша салыстыру")
    others = [b for b in blocks if b.get("key") not in {"Қазақ / Түркі", "Қысқаша салыстыру"}]

    if view.startswith("culture:"):
        code = view.split(":", 1)[1]
        label = CULTURE_CODE_TO_PLAIN.get(code)
        if label:
            block = find_block(label)
            if block:
                add_block(lines, block, short=False)
                return "\n\n".join(lines)
        return "\n\n".join(lines) if lines else ""

    if view == "local":
        if kazakh:
            add_block(lines, kazakh, short=False)
        elif blocks:
            add_block(lines, blocks[0], short=False)
        return "\n\n".join(lines)

    if view == "full":
        for block in blocks:
            add_block(lines, block, short=False)
        return "\n\n".join(lines)

    # default compare view
    if kazakh:
        add_block(lines, kazakh, short=False)
    if others:
        lines.append("<b>Басқа мәдениеттер (қысқаша)</b>")
        for block in others:
            add_block(lines, block, short=True)
    if summary:
        add_block(lines, summary, short=True)
    return "\n\n".join(lines)


async def _send_compare(message: Message, number: str, view: str) -> None:
    text = load_compare_text()
    section = _extract_section(text, number)
    if not section:
        await message.answer(
            "Бұл сан бойынша мәлімет табылмады.",
            reply_markup=main_menu_keyboard(),
        )
        return

    formatted = _render_compare(section, view)
    parts = _split_text(formatted)
    for idx, part in enumerate(parts):
        if idx == len(parts) - 1:
            await message.answer(part, reply_markup=compare_info_keyboard(number, view))
        else:
            await message.answer(part)


@router.message(F.text == MENU_COMPARE)
async def compare_menu(message: Message) -> None:
    await message.answer(
        "Санды таңдаңыз:",
        reply_markup=compare_numbers_keyboard(COMPARE_NUMBERS),
    )


@router.callback_query(F.data == "cmp:list")
async def compare_list(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "Санды таңдаңыз:",
        reply_markup=compare_numbers_keyboard(COMPARE_NUMBERS),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cmp:num:"))
async def compare_show_number(callback: CallbackQuery) -> None:
    number = callback.data.split(":", 2)[2]
    await _send_compare(callback.message, number, "culture:kazakh")
    await callback.answer()


@router.callback_query(F.data.startswith("cmp:view:"))
async def compare_view(callback: CallbackQuery) -> None:
    _, _, number, view = callback.data.split(":", 3)
    await _send_compare(callback.message, number, view)
    await callback.answer()


@router.callback_query(F.data.startswith("cmp:cul:"))
async def compare_culture(callback: CallbackQuery) -> None:
    _, _, number, code = callback.data.split(":", 3)
    await _send_compare(callback.message, number, f"culture:{code}")
    await callback.answer()


@router.callback_query(F.data == "cmp:quiz")
async def compare_quiz_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(
        "Деңгейді таңдаңыз:",
        reply_markup=compare_mode_keyboard(),
    )
    await callback.answer()


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
    questions = load_compare_questions()
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
        reply_markup=compare_question_keyboard(question, index, selected),
    )


async def _finish_quiz(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    correct = data.get("correct_count", 0)
    total = len(data.get("questions", []))
    await state.clear()
    await message.answer(
        f"Салыстырмалы викторина аяқталды!\nНәтиже: {correct}/{total} дұрыс жауап.",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data.startswith("cmpmode:"))
async def compare_quiz_start(callback: CallbackQuery, state: FSMContext) -> None:
    mode = callback.data.split(":", 1)[1]
    questions = _select_questions(mode)
    if not questions:
        await callback.message.answer(
            "Бұл деңгейде сұрақтар табылмады. Басқа деңгейді таңдаңыз.",
            reply_markup=compare_mode_keyboard(),
        )
        await callback.answer()
        return

    await state.set_state(CompareQuizStates.in_quiz)
    await state.update_data(
        mode=mode,
        questions=questions,
        current_index=0,
        correct_count=0,
        selected=[],
    )

    await callback.message.answer(
        f"Салыстырмалы викторина басталды! Сұрақ саны: {len(questions)}.",
        reply_markup=back_menu_keyboard(),
    )
    await _send_question(callback.message, state)
    await callback.answer()


@router.callback_query(CompareQuizStates.in_quiz, F.data.startswith("cmp:ans:"))
async def compare_quiz_answer(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, index_str, choice = callback.data.split(":")
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
        await state.update_data(correct_count=data.get("correct_count", 0) + 1)

    await callback.message.answer(_build_explanation(question, is_correct))

    next_index = current_index + 1
    if next_index >= len(questions):
        await _finish_quiz(callback.message, state)
    else:
        await state.update_data(current_index=next_index, selected=[])
        await _send_question(callback.message, state)
    await callback.answer()


@router.callback_query(CompareQuizStates.in_quiz, F.data.startswith("cmp:toggle:"))
async def compare_quiz_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, index_str, choice = callback.data.split(":")
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
        reply_markup=compare_question_keyboard(question, current_index, selected)
    )
    await callback.answer()


@router.callback_query(CompareQuizStates.in_quiz, F.data.startswith("cmp:submit:"))
async def compare_quiz_submit(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, index_str = callback.data.split(":")
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
        await state.update_data(correct_count=data.get("correct_count", 0) + 1)

    await callback.message.answer(_build_explanation(question, is_correct))

    next_index = current_index + 1
    if next_index >= len(data.get("questions", [])):
        await _finish_quiz(callback.message, state)
    else:
        await state.update_data(current_index=next_index, selected=[])
        await _send_question(callback.message, state)
    await callback.answer()


@router.message(CompareQuizStates.in_quiz)
async def compare_quiz_text_fallback(message: Message) -> None:
    if message.text == MENU_BACK:
        return
    await message.answer("Жауапты төмендегі батырмалар арқылы таңдаңыз.")


@router.message(CompareQuizStates.in_quiz, F.text == MENU_BACK)
async def compare_quiz_back_text(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Мәзірге оралдық.", reply_markup=main_menu_keyboard())
