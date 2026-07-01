"""Обработчики команд и сообщений."""

import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message

from admin_handlers import admin_router
from admin_notify import notify_admin_new_survey
from database import save_survey, upsert_user
from formatting import build_question_message
from admin_auth import is_admin
from keyboards import (
    ADMIN_MENU_BUTTONS,
    BTN_START_SURVEY,
    CALLBACK_CONTINUE,
    CALLBACK_START,
    get_continue_keyboard,
    get_main_keyboard,
    get_start_survey_keyboard,
)
from messaging import answer_photo_with_typing, answer_with_typing, send_with_typing
from states import SurveyStates
from texts import (
    FINAL_TEXT,
    QUESTION_LIST,
    SAVE_ERROR_TEXT,
    WELCOME_IMAGE,
    WELCOME_TEXT_1,
    WELCOME_TEXT_2,
)
from validation import validate_answer

logger = logging.getLogger(__name__)

router = Router(name="main")
router.include_router(admin_router)


async def save_answer(state: FSMContext, key: str, value: str) -> dict:
    """Сохраняет ответ пользователя в FSM data."""
    data = await state.get_data()
    answers = data.get("answers", {})
    answers[key] = value
    await state.update_data(answers=answers)
    return await state.get_data()


async def send_validation_error(message: Message, error_text: str) -> None:
    """Отправляет сообщение об ошибке валидации."""
    await message.answer(error_text, parse_mode=ParseMode.HTML)


async def attach_main_keyboard(message: Message) -> None:
    """Устанавливает постоянное меню."""
    user_id = message.from_user.id
    keyboard = get_main_keyboard(user_id)

    if is_admin(user_id):
        await message.answer(
            "🛠 <b>Меню администратора</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
        return

    await message.answer(
        reply_markup=keyboard,
        text="\u2800",
    )


async def show_welcome_one(message: Message, state: FSMContext) -> None:
    """Показывает первое приветственное сообщение с изображением."""
    await state.set_state(SurveyStates.welcome_one)
    await answer_photo_with_typing(
        message,
        WELCOME_IMAGE,
        WELCOME_TEXT_1,
        reply_markup=get_continue_keyboard(),
    )


async def start_survey_flow(message: Message, state: FSMContext) -> None:
    """Запускает опрос с самого начала."""
    await state.clear()
    user = message.from_user

    try:
        upsert_user(user.id, user.username, user.first_name)
    except Exception:
        await message.answer(SAVE_ERROR_TEXT, parse_mode=ParseMode.HTML)
        return

    logger.info("Запуск опроса: telegram_id=%s", user.id)
    await show_welcome_one(message, state)
    if is_admin(user.id):
        await attach_main_keyboard(message)


async def send_question(message: Message, question_number: int) -> None:
    """Отправляет вопрос с блоком прогресса."""
    text = build_question_message(
        question_number,
        QUESTION_LIST[question_number - 1],
    )
    await answer_with_typing(message, text)


async def finish_survey(message: Message, state: FSMContext) -> None:
    """Сохраняет ответы в PostgreSQL и завершает опрос."""
    data = await state.get_data()
    answers = data.get("answers", {})
    user = message.from_user

    try:
        save_survey(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            answers=answers,
        )
    except Exception:
        await message.answer(SAVE_ERROR_TEXT, parse_mode=ParseMode.HTML)
        return

    username_display = f"@{user.username}" if user.username else "—"
    logger.info(
        "Опрос завершён: имя=%s, username=%s, telegram_id=%s",
        user.first_name or "—",
        username_display,
        user.id,
    )

    await notify_admin_new_survey(
        bot=message.bot,
        user=user,
        answers=answers,
        started_at=data.get("survey_started_at"),
    )

    await state.set_state(SurveyStates.finished)
    await answer_with_typing(
        message,
        FINAL_TEXT,
        reply_markup=get_main_keyboard(user.id),
    )
    await state.clear()


async def process_question_answer(
    message: Message,
    state: FSMContext,
    question_num: int,
    answer_key: str,
    next_state: State | None,
    next_question_num: int | None,
) -> None:
    """Обрабатывает ответ на вопрос и переходит к следующему шагу."""
    validation_error = validate_answer(message)
    if validation_error:
        await send_validation_error(message, validation_error)
        return

    answer = message.text.strip()
    await save_answer(state, answer_key, answer)
    logger.info(
        "Ответ на вопрос %s: user_id=%s",
        question_num,
        message.from_user.id,
    )

    if next_question_num is None:
        await finish_survey(message, state)
        return

    await state.set_state(next_state)
    await send_question(message, next_question_num)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Запускает опрос с первого приветственного сообщения."""
    await state.clear()
    user = message.from_user
    logger.info(
        "Новый пользователь: telegram_id=%s, username=%s, имя=%s",
        user.id,
        user.username or "—",
        user.first_name or "—",
    )

    try:
        upsert_user(user.id, user.username, user.first_name)
    except Exception:
        await message.answer(SAVE_ERROR_TEXT, parse_mode=ParseMode.HTML)
        return

    await show_welcome_one(message, state)
    await attach_main_keyboard(message)


@router.message(F.text == BTN_START_SURVEY)
async def on_start_survey_button(message: Message, state: FSMContext) -> None:
    """Запускает опрос по кнопке главного меню."""
    await start_survey_flow(message, state)


@router.callback_query(SurveyStates.welcome_one, F.data == CALLBACK_CONTINUE)
async def on_continue(callback: CallbackQuery, state: FSMContext) -> None:
    """Показывает второе приветственное сообщение."""
    await callback.answer()
    await state.set_state(SurveyStates.welcome_two)
    await send_with_typing(
        callback.message.bot,
        callback.message.chat.id,
        WELCOME_TEXT_2,
        reply_markup=get_start_survey_keyboard(),
    )


@router.callback_query(SurveyStates.welcome_two, F.data == CALLBACK_START)
async def on_start_survey(callback: CallbackQuery, state: FSMContext) -> None:
    """Начинает опрос — отправляет первый вопрос."""
    await callback.answer()
    user = callback.from_user
    logger.info("Начало опроса: telegram_id=%s", user.id)

    await state.update_data(survey_started_at=datetime.now().isoformat())
    await state.set_state(SurveyStates.question_1)
    text = build_question_message(1, QUESTION_LIST[0])
    await send_with_typing(callback.message.bot, callback.message.chat.id, text)


def _not_menu_button() -> F:
    """Исключает нажатия кнопок главного меню из обработки ответов."""
    return ~F.text.in_({BTN_START_SURVEY, *ADMIN_MENU_BUTTONS})


@router.message(SurveyStates.question_1, _not_menu_button())
async def handle_question_1_answer(message: Message, state: FSMContext) -> None:
    """Обрабатывает ответ на вопрос 1."""
    await process_question_answer(
        message, state, 1, "q1", SurveyStates.question_2, 2,
    )


@router.message(SurveyStates.question_2, _not_menu_button())
async def handle_question_2_answer(message: Message, state: FSMContext) -> None:
    """Обрабатывает ответ на вопрос 2."""
    await process_question_answer(
        message, state, 2, "q2", SurveyStates.question_3, 3,
    )


@router.message(SurveyStates.question_3, _not_menu_button())
async def handle_question_3_answer(message: Message, state: FSMContext) -> None:
    """Обрабатывает ответ на вопрос 3."""
    await process_question_answer(
        message, state, 3, "q3", SurveyStates.question_4, 4,
    )


@router.message(SurveyStates.question_4, _not_menu_button())
async def handle_question_4_answer(message: Message, state: FSMContext) -> None:
    """Обрабатывает ответ на вопрос 4."""
    await process_question_answer(
        message, state, 4, "q4", SurveyStates.question_5, 5,
    )


@router.message(SurveyStates.question_5, _not_menu_button())
async def handle_question_5_answer(message: Message, state: FSMContext) -> None:
    """Обрабатывает ответ на вопрос 5."""
    await process_question_answer(
        message, state, 5, "q5", SurveyStates.question_6, 6,
    )


@router.message(SurveyStates.question_6, _not_menu_button())
async def handle_question_6_answer(message: Message, state: FSMContext) -> None:
    """Обрабатывает ответ на вопрос 6."""
    await process_question_answer(
        message, state, 6, "q6", SurveyStates.question_7, 7,
    )


@router.message(SurveyStates.question_7, _not_menu_button())
async def handle_question_7_answer(message: Message, state: FSMContext) -> None:
    """Обрабатывает ответ на вопрос 7."""
    await process_question_answer(message, state, 7, "q7", None, None)
