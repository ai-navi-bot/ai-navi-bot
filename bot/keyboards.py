"""Клавиатуры бота."""

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from admin_auth import is_admin

CALLBACK_CONTINUE = "survey:continue"
CALLBACK_START = "survey:start"

BTN_START_SURVEY = "📝 Пройти опрос"
BTN_ADMIN_STATS = "📊 Статистика"
BTN_ADMIN_EXCEL = "📄 Скачать Excel"
BTN_ADMIN_LAST = "👥 Последние анкеты"

ADMIN_MENU_BUTTONS = frozenset({
    BTN_ADMIN_STATS,
    BTN_ADMIN_EXCEL,
    BTN_ADMIN_LAST,
})


def get_user_main_keyboard() -> ReplyKeyboardMarkup:
    """Постоянное меню обычного пользователя."""
    builder = ReplyKeyboardBuilder()
    builder.button(text=BTN_START_SURVEY)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_admin_main_keyboard() -> ReplyKeyboardMarkup:
    """Постоянное меню администратора."""
    builder = ReplyKeyboardBuilder()
    builder.button(text=BTN_START_SURVEY)
    builder.button(text=BTN_ADMIN_STATS)
    builder.button(text=BTN_ADMIN_EXCEL)
    builder.button(text=BTN_ADMIN_LAST)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """Возвращает меню в зависимости от роли пользователя."""
    if is_admin(user_id):
        return get_admin_main_keyboard()
    return get_user_main_keyboard()


def get_continue_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после первого приветственного сообщения."""
    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ Продолжить", callback_data=CALLBACK_CONTINUE)
    return builder.as_markup()


def get_start_survey_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура перед началом опроса."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Начнём? 👇", callback_data=CALLBACK_START)
    return builder.as_markup()
