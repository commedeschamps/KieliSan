import random
from pathlib import Path
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile

from bot.constants import MENU_INFO
from bot.keyboards.system.menu import main_menu_keyboard
from bot.keyboards.content.numbers import (
    numbers_keyboard,
    number_info_keyboard,
)
from bot.utils.loader import load_sacred_numbers

router = Router()
BASE_DIR = Path(__file__).resolve().parents[3]
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
CAPTION_LIMIT = 1024


@router.message(F.text == MENU_INFO)
async def numbers_menu(message: Message) -> None:
    data = load_sacred_numbers()
    if not data:
        await message.answer(
            "Өкінішке қарай, контент табылмады.",
            reply_markup=main_menu_keyboard(),
        )
        return

    numbers = sorted(data.keys(), key=lambda n: int(n))
    await message.answer(
        "Қай сан туралы білгіңіз келеді?",
        reply_markup=numbers_keyboard(numbers),
    )


def _format_block(text: str) -> str:
    if ": " in text:
        label, rest = text.split(": ", 1)
        return f"<b>{label}:</b> {rest}"
    return text


def _render_short(item: dict) -> str:
    short_text = item.get("short") or item.get("description", "")
    return _format_block(short_text) if short_text else ""


def _render_full(item: dict) -> str:
    blocks = [
        _format_block(item.get("description", "")),
        _format_block(item.get("expressions", "")),
        _format_block(item.get("example", "")),
        _format_block(item.get("fact", "")),
    ]
    return "\n\n".join([block for block in blocks if block])


def _render_card(number: str, item: dict, mode: str) -> str:
    title = f"<b>{number} саны</b>"
    content = _render_full(item) if mode == "full" else _render_short(item)

    parts = [title]
    if content:
        parts.append(content)
    return "\n\n".join(parts)


def _find_image_path(number: str) -> Optional[Path]:
    for ext in IMAGE_EXTS:
        candidate = BASE_DIR / "assets" / "numbers" / f"num_{number}{ext}"
        if candidate.exists():
            return candidate
    return None


async def _send_card(message: Message, number: str, item: dict, mode: str) -> None:
    text = _render_card(number, item, mode)
    image_path = _find_image_path(number)
    if image_path:
        caption = text
        if len(caption) > CAPTION_LIMIT:
            caption = _render_card(number, item, "short")
            if mode == "full":
                caption = f"{caption}\n\n(Толық нұсқа төменде.)"
        await message.answer_photo(
            FSInputFile(image_path),
            caption=caption,
            reply_markup=number_info_keyboard(number, mode),
        )
        if mode == "full" and len(text) > CAPTION_LIMIT:
            await message.answer(text)
    else:
        await message.answer(text, reply_markup=number_info_keyboard(number, mode))


async def _edit_card(message: Message, number: str, item: dict, mode: str) -> None:
    text = _render_card(number, item, mode)
    if message.photo:
        caption = text
        if len(caption) > CAPTION_LIMIT:
            caption = _render_card(number, item, "short")
            if mode == "full":
                caption = f"{caption}\n\n(Толық нұсқа төменде.)"
        await message.edit_caption(
            caption=caption,
            reply_markup=number_info_keyboard(number, mode),
        )
        if mode == "full" and len(text) > CAPTION_LIMIT:
            await message.answer(text)
    else:
        await message.edit_text(
            text,
            reply_markup=number_info_keyboard(number, mode),
        )


@router.callback_query(F.data == "num:random")
async def number_random(callback: CallbackQuery) -> None:
    data = load_sacred_numbers()
    if not data:
        await callback.message.answer(
            "Өкінішке қарай, контент табылмады.",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    number = random.choice(list(data.keys()))
    await _send_card(callback.message, number, data[number], "short")
    await callback.answer()


@router.callback_query(F.data == "num:list")
async def number_list(callback: CallbackQuery) -> None:
    data = load_sacred_numbers()
    if not data:
        await callback.message.answer(
            "Өкінішке қарай, контент табылмады.",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    numbers = sorted(data.keys(), key=lambda n: int(n))
    await callback.message.answer(
        "Қай сан туралы білгіңіз келеді?",
        reply_markup=numbers_keyboard(numbers),
    )
    await callback.answer()


@router.callback_query(F.data == "num:next")
async def number_next(callback: CallbackQuery) -> None:
    data = load_sacred_numbers()
    if not data:
        await callback.message.answer(
            "Өкінішке қарай, контент табылмады.",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    number = random.choice(list(data.keys()))
    await _send_card(callback.message, number, data[number], "short")
    await callback.answer()


@router.callback_query(F.data.startswith("num:toggle:"))
async def number_toggle(callback: CallbackQuery) -> None:
    _, _, number, mode = callback.data.split(":", 3)
    data = load_sacred_numbers()
    item = data.get(number)
    if not item:
        await callback.message.answer(
            "Бұл сан бойынша мәлімет табылмады.",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    new_mode = "full" if mode == "short" else "short"
    try:
        await _edit_card(callback.message, number, item, new_mode)
    except Exception:
        await _send_card(callback.message, number, item, new_mode)
    await callback.answer()


@router.callback_query(F.data.startswith("num:help:"))
async def number_help(callback: CallbackQuery) -> None:
    _, _, number = callback.data.split(":", 2)
    data = load_sacred_numbers()
    item = data.get(number)
    if not item:
        await callback.message.answer(
            "Бұл сан бойынша мәлімет табылмады.",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    short_text = _render_short(item)
    if not short_text:
        await callback.answer("Қысқа мәтін табылмады.", show_alert=True)
        return

    await callback.message.answer(
        "\n\n".join([f"<b>{number} саны</b>", short_text])
    )
    await callback.answer()


@router.callback_query(F.data.startswith("num:"))
async def number_show(callback: CallbackQuery) -> None:
    number = callback.data.split(":", 1)[1]
    if number in {"random", "next", "list"} or not number.isdigit():
        await callback.answer()
        return

    data = load_sacred_numbers()
    item = data.get(number)
    if not item:
        await callback.message.answer(
            "Бұл сан бойынша мәлімет табылмады.",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    await _send_card(callback.message, number, item, "short")
    await callback.answer()
