"""Валидация ответов пользователя."""

from aiogram.enums import ContentType
from aiogram.types import Message

from texts import EMPTY_ANSWER_TEXT, INVALID_ANSWER_TYPE_TEXT

NON_TEXT_CONTENT_TYPES = {
    ContentType.STICKER,
    ContentType.PHOTO,
    ContentType.VIDEO,
    ContentType.VOICE,
    ContentType.ANIMATION,
    ContentType.DOCUMENT,
    ContentType.LOCATION,
    ContentType.CONTACT,
}


def validate_answer(message: Message) -> str | None:
    """Возвращает текст ошибки или None, если ответ корректен."""
    if message.content_type in NON_TEXT_CONTENT_TYPES:
        return INVALID_ANSWER_TYPE_TEXT

    if message.content_type != ContentType.TEXT:
        return INVALID_ANSWER_TYPE_TEXT

    if not message.text or not message.text.strip():
        return EMPTY_ANSWER_TEXT

    return None
