"""Экспорт данных опроса в Excel."""

import logging
from pathlib import Path

from openpyxl import Workbook

from database import SurveyRecord, get_all_surveys

logger = logging.getLogger(__name__)

RESPONSES_FILE: Path = Path(__file__).parent / "data" / "responses.xlsx"

HEADERS: list[str] = [
    "Дата",
    "Telegram ID",
    "Username",
    "Имя",
    "Ответ 1",
    "Ответ 2",
    "Ответ 3",
    "Ответ 4",
    "Ответ 5",
    "Ответ 6",
    "Ответ 7",
]


def _survey_to_row(survey: SurveyRecord) -> list[str | int]:
    """Преобразует запись опроса в строку для Excel."""
    return [
        survey.created_at,
        survey.telegram_id,
        survey.username,
        survey.first_name,
        survey.answer_1,
        survey.answer_2,
        survey.answer_3,
        survey.answer_4,
        survey.answer_5,
        survey.answer_6,
        survey.answer_7,
    ]


def export_to_excel() -> Path:
    """Создаёт Excel-файл из всех записей PostgreSQL и возвращает путь к нему."""
    try:
        surveys = get_all_surveys()
        RESPONSES_FILE.parent.mkdir(parents=True, exist_ok=True)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Responses"
        sheet.append(HEADERS)

        for survey in surveys:
            sheet.append(_survey_to_row(survey))

        workbook.save(RESPONSES_FILE)
        logger.info(
            "Экспорт в Excel завершён: %s, записей: %s",
            RESPONSES_FILE,
            len(surveys),
        )
        return RESPONSES_FILE
    except Exception:
        logger.exception("Ошибка экспорта данных в Excel")
        raise
