"""Проверка прав администратора."""

from config import Config


def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором."""
    return user_id in Config().admin_ids


def get_admin_ids() -> frozenset[int]:
    """Возвращает Telegram ID всех администраторов."""
    return Config().admin_ids


def get_admin_id() -> int | None:
    """Возвращает Telegram ID первого администратора."""
    return Config().admin_id
