"""Вспомогательные функции отправки сообщений."""

import asyncio
from pathlib import Path

from aiogram import Bot
from aiogram.enums import ChatAction, ParseMode
from aiogram.types import FSInputFile, Message, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup

TYPING_DELAY_SECONDS = 0.7

ReplyMarkup = InlineKeyboardMarkup | ReplyKeyboardMarkup | None


async def show_typing(bot: Bot, chat_id: int) -> None:
    """Показывает индикатор «печатает...» с небольшой задержкой."""
    await bot.send_chat_action(chat_id, ChatAction.TYPING)
    await asyncio.sleep(TYPING_DELAY_SECONDS)


async def show_upload_photo(bot: Bot, chat_id: int) -> None:
    """Показывает индикатор загрузки фото с небольшой задержкой."""
    await bot.send_chat_action(chat_id, ChatAction.UPLOAD_PHOTO)
    await asyncio.sleep(TYPING_DELAY_SECONDS)


async def answer_with_typing(
    message: Message,
    text: str,
    reply_markup: ReplyMarkup = None,
) -> Message:
    """Отправляет ответ с эффектом печати и HTML-разметкой."""
    await show_typing(message.bot, message.chat.id)
    return await message.answer(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )


async def answer_photo_with_typing(
    message: Message,
    photo_path: Path,
    caption: str,
    reply_markup: ReplyMarkup = None,
) -> Message:
    """Отправляет фото с подписью, эффектом загрузки и HTML-разметкой."""
    await show_upload_photo(message.bot, message.chat.id)
    return await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )


async def send_with_typing(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_markup: ReplyMarkup = None,
) -> Message:
    """Отправляет сообщение в чат с эффектом печати."""
    await show_typing(bot, chat_id)
    return await bot.send_message(
        chat_id,
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )
