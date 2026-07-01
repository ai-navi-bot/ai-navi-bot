"""Состояния FSM для диалогов бота."""

from aiogram.fsm.state import State, StatesGroup


class SurveyStates(StatesGroup):
    """Состояния сценария прохождения опроса."""

    welcome_one = State()
    welcome_two = State()
    question_1 = State()
    question_2 = State()
    question_3 = State()
    question_4 = State()
    question_5 = State()
    question_6 = State()
    question_7 = State()
    finished = State()
