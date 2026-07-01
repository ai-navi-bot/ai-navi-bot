"""Форматирование административных сообщений."""

from database import SurveyBrief, SurveyStatistics, UserRecord, UserSurveyDetail
from formatting import SEPARATOR


def build_statistics_message(stats: SurveyStatistics) -> str:
    """Формирует HTML-сообщение со статистикой опроса."""
    last_date = stats.last_survey_date or "—"

    return (
        f"{SEPARATOR}\n\n"
        "📊 <b>Статистика</b>\n\n"
        f"👥 <b>Всего пользователей:</b> {stats.total_users}\n"
        f"📝 <b>Всего прохождений:</b> {stats.total_surveys}\n\n"
        f"📅 <b>Сегодня:</b> {stats.surveys_today}\n"
        f"📆 <b>За неделю:</b> {stats.surveys_week}\n"
        f"🗓 <b>За месяц:</b> {stats.surveys_month}\n\n"
        f"🕐 <b>Последняя анкета:</b>\n{last_date}\n\n"
        f"{SEPARATOR}"
    )


def build_last_surveys_message(surveys: list[SurveyBrief]) -> str:
    """Формирует HTML-сообщение со списком последних анкет."""
    if not surveys:
        return (
            f"{SEPARATOR}\n\n"
            "👥 <b>Последние анкеты</b>\n\n"
            "Пока нет данных.\n\n"
            f"{SEPARATOR}"
        )

    lines: list[str] = []
    for index, survey in enumerate(surveys, start=1):
        username = (
            f"@{survey.username}"
            if survey.username and survey.username != "—"
            else "—"
        )
        lines.append(
            f"<b>{index}.</b> #{survey.survey_id} — {survey.first_name}\n"
            f"ID: {survey.telegram_id} | {username}\n"
            f"📅 {survey.created_at}",
        )

    block = "\n\n".join(lines)
    return (
        f"{SEPARATOR}\n\n"
        "👥 <b>Последние 20 анкет</b>\n\n"
        f"{block}\n\n"
        f"{SEPARATOR}"
    )


def build_user_search_result(
    user: UserRecord,
    surveys: list[UserSurveyDetail],
) -> str:
    """Формирует HTML-сообщение с прохождениями пользователя."""
    username = (
        f"@{user.username}"
        if user.username and user.username != "—"
        else "—"
    )

    header = (
        f"{SEPARATOR}\n\n"
        "🔍 <b>Результат поиска</b>\n\n"
        f"👤 <b>{user.first_name}</b>\n"
        f"Username: {username}\n"
        f"Telegram ID: {user.telegram_id}\n"
        f"Первый визит: {user.first_seen}\n"
        f"Прохождений: {user.surveys_count}\n\n"
    )

    if not surveys:
        return header + "Анкеты не найдены.\n\n" + SEPARATOR

    lines: list[str] = []
    for survey in surveys:
        answers_preview = survey.answers[0][:80] if survey.answers[0] != "—" else "—"
        lines.append(
            f"<b>#{survey.survey_id}</b> — {survey.created_at}\n"
            f"Ответ 1: {answers_preview}",
        )

    return header + "\n\n".join(lines) + f"\n\n{SEPARATOR}"


def build_settings_message(admin_id: int | None, db_path: str) -> str:
    """Формирует HTML-сообщение с настройками бота."""
    admin_display = str(admin_id) if admin_id else "не задан"

    return (
        f"{SEPARATOR}\n\n"
        "⚙ <b>Настройки</b>\n\n"
        f"🆔 <b>ADMIN_ID:</b> {admin_display}\n"
        f"💾 <b>База данных:</b>\n<code>{db_path}</code>\n\n"
        "Повторное прохождение опроса: <b>включено</b>\n"
        "Ограничение «одна анкета»: <b>отключено</b>\n\n"
        f"{SEPARATOR}"
    )
