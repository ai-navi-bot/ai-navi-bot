"""Обработчики административных команд."""

import logging

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, Message

from admin_auth import is_admin
from admin_formatting import build_last_surveys_message, build_statistics_message
from database import get_last_surveys, get_statistics
from excel import export_to_excel
from keyboards import BTN_ADMIN_EXCEL, BTN_ADMIN_LAST, BTN_ADMIN_STATS
from texts import ADMIN_ACCESS_DENIED, SAVE_ERROR_TEXT

logger = logging.getLogger(__name__)

admin_router = Router(name="admin")


def _check_admin(user_id: int) -> bool:
    """Проверяет права администратора."""
    return is_admin(user_id)


async def deny_admin_access(message: Message) -> None:
    """Отправляет сообщение об отсутствии доступа."""
    await message.answer(ADMIN_ACCESS_DENIED, parse_mode=ParseMode.HTML)


@admin_router.message(F.text == BTN_ADMIN_STATS)
async def on_admin_statistics(message: Message) -> None:
    """Показывает статистику опроса."""
    if not _check_admin(message.from_user.id):
        await deny_admin_access(message)
        return

    try:
        stats = get_statistics()
    except Exception:
        await message.answer(SAVE_ERROR_TEXT, parse_mode=ParseMode.HTML)
        return

    logger.info("Запрошена статистика администратором")
    await message.answer(
        build_statistics_message(stats),
        parse_mode=ParseMode.HTML,
    )


@admin_router.message(F.text == BTN_ADMIN_EXCEL)
async def on_admin_download_excel(message: Message) -> None:
    """Отправляет файл Excel администратору."""
    if not _check_admin(message.from_user.id):
        await deny_admin_access(message)
        return

    try:
        excel_path = export_to_excel()
        document = FSInputFile(excel_path)
        await message.answer_document(document)
        logger.info("Excel сгенерирован и отправлен администратору")
    except Exception:
        logger.exception("Ошибка отправки Excel администратору")
        await message.answer(SAVE_ERROR_TEXT, parse_mode=ParseMode.HTML)


@admin_router.message(F.text == BTN_ADMIN_LAST)
async def on_admin_last_surveys(message: Message) -> None:
    """Показывает последние 20 анкет."""
    if not _check_admin(message.from_user.id):
        await deny_admin_access(message)
        return

    try:
        surveys = get_last_surveys(limit=20)
    except Exception:
        await message.answer(SAVE_ERROR_TEXT, parse_mode=ParseMode.HTML)
        return

    logger.info("Запрошен список последних анкет")
    await message.answer(
        build_last_surveys_message(surveys),
        parse_mode=ParseMode.HTML,
    )
