"""Форматирование сообщений бота."""

SEPARATOR = "━━━━━━━━━━━━━━"
TOTAL_QUESTIONS = 7
PROGRESS_BAR_LENGTH = 10


def format_progress_bar(question_number: int, total: int = TOTAL_QUESTIONS) -> str:
    """Формирует строку прогресс-бара с процентом."""
    percent = round(question_number / total * 100)
    filled = min(round(percent / 10), PROGRESS_BAR_LENGTH)
    bar = "█" * filled + "░" * (PROGRESS_BAR_LENGTH - filled)
    return f"{bar} {percent}%"


def build_question_message(question_number: int, question_text: str) -> str:
    """Собирает сообщение с заголовком, текстом вопроса и прогресс-баром."""
    header = f"<b>Вопрос {question_number} из {TOTAL_QUESTIONS}</b>"
    body = f"<b>{question_text}</b>"
    progress = format_progress_bar(question_number)
    return f"{header}\n\n{body}\n\n{progress}"
