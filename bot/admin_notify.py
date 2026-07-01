"""Уведомления администратора о новых анкетах."""

import logging
from datetime import datetime

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import User

from admin_auth import get_admin_ids
from formatting import SEPARATOR

logger = logging.getLogger(__name__)


def format_survey_duration(started_at: str | None) -> str:
    """Форматирует длительность прохождения опроса."""
    if not started_at:
        return "—"

    start_time = datetime.fromisoformat(started_at)
    delta = datetime.now() - start_time
    total_seconds = int(delta.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)

    if minutes:
        return f"{minutes} мин {seconds} сек"
    return f"{seconds} сек"


def build_admin_notification(
    user: User,
    answers: dict[str, str],
    survey_date: str,
    duration: str,
) -> str:
    """Формирует HTML-сообщение о новой анкете для администратора."""
    username = f"@{user.username}" if user.username else "—"
    first_name = user.first_name or "—"

    answers_block = "\n\n".join(
        f"<b>Ответ {index}</b>\n\n{answers.get(f'q{index}', '—')}"
        for index in range(1, 8)
    )

    return (
        f"{SEPARATOR}\n\n"
        "🎉 <b>Новая анкета</b>\n\n"
        f"👤 <b>Имя:</b>\n{first_name}\n\n"
        f"🔗 <b>Username:</b>\n{username}\n\n"
        f"🆔 <b>Telegram ID:</b>\n{user.id}\n\n"
        f"📅 <b>Дата:</b>\n{survey_date}\n\n"
        f"⏱ <b>Время прохождения:</b>\n{duration}\n\n"
        f"{SEPARATOR}\n\n"
        f"{answers_block}\n\n"
        f"{SEPARATOR}"
    )


async def notify_admin_new_survey(
    bot: Bot,
    user: User,
    answers: dict[str, str],
    started_at: str | None,
) -> None:
    """Отправляет администратору уведомление о новой анкете."""
    admin_ids = get_admin_ids()
    if not admin_ids:
        return

    survey_date = datetime.now().strftime("%d.%m.%Y %H:%M")
    duration = format_survey_duration(started_at)
    text = build_admin_notification(user, answers, survey_date, duration)

    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, text, parse_mode=ParseMode.HTML)
            logger.info(
                "Уведомление админу отправлено: admin_id=%s, user_id=%s",
                admin_id,
                user.id,
            )
        except Exception:
            logger.exception(
                "Ошибка отправки уведомления админу %s: telegram_id=%s",
                admin_id,
                user.id,
            )
