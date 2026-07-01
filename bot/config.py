"""Конфигурация приложения."""

import logging
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _parse_admin_ids() -> frozenset[int]:
    """Парсит список ADMIN_ID из переменных окружения."""
    raw_value = os.getenv("ADMIN_ID", "").strip()
    if not raw_value:
        return frozenset()

    admin_ids: set[int] = set()
    for part in raw_value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            admin_ids.add(int(part))
        except ValueError:
            logger.warning("Некорректное значение ADMIN_ID: %s", part)

    return frozenset(admin_ids)


def _parse_database_url() -> str:
    """Возвращает DATABASE_URL из переменных окружения."""
    return os.getenv("DATABASE_URL", "").strip()


@dataclass(frozen=True)
class Config:
    """Настройки бота, загружаемые из переменных окружения."""

    bot_token: str = os.getenv("BOT_TOKEN", "").strip()
    database_url: str = field(default_factory=_parse_database_url)
    admin_ids: frozenset[int] = field(default_factory=_parse_admin_ids)

    @property
    def admin_id(self) -> int | None:
        """Первый ID администратора для обратной совместимости."""
        if not self.admin_ids:
            return None
        return next(iter(sorted(self.admin_ids)))
