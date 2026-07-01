"""Работа с базой данных PostgreSQL."""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from config import Config
from models import Base, Survey, User

logger = logging.getLogger(__name__)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

ANSWER_KEYS: tuple[str, ...] = (
    "q1", "q2", "q3", "q4", "q5", "q6", "q7",
)

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


@dataclass(frozen=True)
class SurveyStatistics:
    """Расширенная статистика по опросам."""

    total_users: int
    total_surveys: int
    surveys_today: int
    surveys_week: int
    surveys_month: int
    last_survey_date: str | None


@dataclass(frozen=True)
class SurveyBrief:
    """Краткая информация о прохождении опроса."""

    survey_id: int
    created_at: str
    telegram_id: int
    username: str
    first_name: str


@dataclass(frozen=True)
class SurveyRecord:
    """Полная запись опроса для экспорта."""

    id: int
    created_at: str
    telegram_id: int
    username: str
    first_name: str
    answer_1: str
    answer_2: str
    answer_3: str
    answer_4: str
    answer_5: str
    answer_6: str
    answer_7: str


@dataclass(frozen=True)
class UserRecord:
    """Запись пользователя."""

    id: int
    telegram_id: int
    username: str
    first_name: str
    first_seen: str
    surveys_count: int


@dataclass(frozen=True)
class UserSurveyDetail:
    """Детали одного прохождения пользователя."""

    survey_id: int
    created_at: str
    answers: tuple[str, ...]


def _normalize_database_url(url: str) -> str:
    """Приводит DATABASE_URL к формату SQLAlchemy + psycopg2."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://") and "+psycopg2" not in url:
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def _get_engine() -> Engine:
    """Возвращает singleton-движок SQLAlchemy."""
    global _engine, _SessionLocal

    if _engine is not None:
        return _engine

    database_url = _normalize_database_url(Config().database_url)
    if not database_url:
        raise RuntimeError(
            "Переменная окружения DATABASE_URL не задана. "
            "Укажите postgresql://... в .env или Variables Railway.",
        )

    _engine = create_engine(database_url, pool_pre_ping=True)
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    return _engine


def _get_session() -> Session:
    """Создаёт сессию SQLAlchemy."""
    _get_engine()
    if _SessionLocal is None:
        raise RuntimeError("Сессия базы данных не инициализирована")
    return _SessionLocal()


def _now() -> datetime:
    """Возвращает текущую дату и время."""
    return datetime.now()


def _format_datetime(value: datetime | None) -> str:
    """Форматирует дату для отображения."""
    if value is None:
        return ""
    return value.strftime(DATE_FORMAT)


def _upsert_user_in_session(
    session: Session,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    first_seen: datetime | None = None,
) -> int:
    """Создаёт или обновляет пользователя, возвращает user_id."""
    now = first_seen or _now()
    stmt = (
        insert(User)
        .values(
            telegram_id=telegram_id,
            username=username or "",
            first_name=first_name or "",
            first_seen=now,
        )
        .on_conflict_do_update(
            index_elements=[User.telegram_id],
            set_={
                "username": username or "",
                "first_name": first_name or "",
            },
        )
        .returning(User.id)
    )
    user_id = session.execute(stmt).scalar_one()
    return int(user_id)


def _survey_to_record(survey: Survey, user: User) -> SurveyRecord:
    """Преобразует ORM-объекты в SurveyRecord."""
    return SurveyRecord(
        id=survey.id,
        created_at=_format_datetime(survey.created_at),
        telegram_id=user.telegram_id,
        username=user.username or "",
        first_name=user.first_name or "",
        answer_1=survey.answer_1 or "",
        answer_2=survey.answer_2 or "",
        answer_3=survey.answer_3 or "",
        answer_4=survey.answer_4 or "",
        answer_5=survey.answer_5 or "",
        answer_6=survey.answer_6 or "",
        answer_7=survey.answer_7 or "",
    )


def init_db() -> None:
    """Создаёт таблицы PostgreSQL при запуске."""
    try:
        engine = _get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("База данных PostgreSQL инициализирована")
    except SQLAlchemyError:
        logger.exception("Ошибка инициализации базы данных PostgreSQL")
        raise


def upsert_user(
    telegram_id: int,
    username: str | None,
    first_name: str | None,
) -> int:
    """Регистрирует или обновляет пользователя."""
    try:
        with _get_session() as session:
            with session.begin():
                user_id = _upsert_user_in_session(
                    session,
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                )
            return user_id
    except SQLAlchemyError:
        logger.exception(
            "Ошибка upsert пользователя: telegram_id=%s",
            telegram_id,
        )
        raise


def save_survey(
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    answers: dict[str, str],
) -> int:
    """Сохраняет новое прохождение опроса."""
    try:
        created_at = _now()
        answer_values = {f"answer_{index}": answers.get(key, "") for index, key in enumerate(ANSWER_KEYS, start=1)}

        with _get_session() as session:
            with session.begin():
                user_id = _upsert_user_in_session(
                    session,
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                )
                survey = Survey(
                    user_id=user_id,
                    created_at=created_at,
                    **answer_values,
                )
                session.add(survey)
                session.flush()
                survey_id = int(survey.id)

        logger.info(
            "Сохранение опроса: telegram_id=%s, survey_id=%s",
            telegram_id,
            survey_id,
        )
        return survey_id
    except SQLAlchemyError:
        logger.exception(
            "Ошибка сохранения опроса: telegram_id=%s",
            telegram_id,
        )
        raise


def _count_surveys_since(session: Session, since: datetime) -> int:
    """Считает опросы начиная с указанной даты."""
    count = session.scalar(
        select(func.count())
        .select_from(Survey)
        .where(Survey.created_at >= since),
    )
    return int(count or 0)


def get_statistics() -> SurveyStatistics:
    """Возвращает расширенную статистику."""
    try:
        now = _now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)

        with _get_session() as session:
            total_users = session.scalar(select(func.count()).select_from(User)) or 0
            total_surveys = session.scalar(select(func.count()).select_from(Survey)) or 0
            last_date = session.scalar(select(func.max(Survey.created_at)))

            surveys_today = _count_surveys_since(session, today_start)
            surveys_week = _count_surveys_since(session, week_start)
            surveys_month = _count_surveys_since(session, month_start)

        return SurveyStatistics(
            total_users=int(total_users),
            total_surveys=int(total_surveys),
            surveys_today=surveys_today,
            surveys_week=surveys_week,
            surveys_month=surveys_month,
            last_survey_date=_format_datetime(last_date) or None,
        )
    except SQLAlchemyError:
        logger.exception("Ошибка получения статистики из PostgreSQL")
        raise


def get_last_surveys(limit: int = 20) -> list[SurveyBrief]:
    """Возвращает последние прохождения опроса."""
    try:
        with _get_session() as session:
            rows = session.execute(
                select(Survey, User)
                .join(User, User.id == Survey.user_id)
                .order_by(Survey.id.desc())
                .limit(limit),
            ).all()

        return [
            SurveyBrief(
                survey_id=survey.id,
                created_at=_format_datetime(survey.created_at),
                telegram_id=user.telegram_id,
                username=user.username or "—",
                first_name=user.first_name or "—",
            )
            for survey, user in rows
        ]
    except SQLAlchemyError:
        logger.exception("Ошибка получения последних анкет")
        raise


def get_all_surveys() -> list[SurveyRecord]:
    """Возвращает все записи опросов."""
    try:
        with _get_session() as session:
            rows = session.execute(
                select(Survey, User)
                .join(User, User.id == Survey.user_id)
                .order_by(Survey.id.asc()),
            ).all()

        return [_survey_to_record(survey, user) for survey, user in rows]
    except SQLAlchemyError:
        logger.exception("Ошибка получения всех опросов из PostgreSQL")
        raise


def find_user(query: str) -> UserRecord | None:
    """Ищет пользователя по Telegram ID или username."""
    try:
        cleaned = query.strip().lstrip("@")
        if not cleaned:
            return None

        with _get_session() as session:
            stmt = (
                select(
                    User,
                    func.count(Survey.id).label("surveys_count"),
                )
                .outerjoin(Survey, Survey.user_id == User.id)
                .group_by(User.id)
            )

            if cleaned.isdigit():
                stmt = stmt.where(User.telegram_id == int(cleaned))
            else:
                stmt = stmt.where(func.lower(User.username) == cleaned.lower())

            row = session.execute(stmt).first()

            if row is None:
                return None

            user, surveys_count = row
            return UserRecord(
                id=user.id,
                telegram_id=user.telegram_id,
                username=user.username or "—",
                first_name=user.first_name or "—",
                first_seen=_format_datetime(user.first_seen),
                surveys_count=int(surveys_count or 0),
            )
    except SQLAlchemyError:
        logger.exception("Ошибка поиска пользователя: query=%s", query)
        raise


def get_user_surveys(user_id: int) -> list[UserSurveyDetail]:
    """Возвращает все прохождения пользователя."""
    try:
        with _get_session() as session:
            surveys = session.scalars(
                select(Survey)
                .where(Survey.user_id == user_id)
                .order_by(Survey.id.desc()),
            ).all()

        return [
            UserSurveyDetail(
                survey_id=survey.id,
                created_at=_format_datetime(survey.created_at),
                answers=tuple(
                    getattr(survey, f"answer_{index}") or "—"
                    for index in range(1, 8)
                ),
            )
            for survey in surveys
        ]
    except SQLAlchemyError:
        logger.exception("Ошибка получения прохождений user_id=%s", user_id)
        raise
