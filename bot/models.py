"""SQLAlchemy-модели PostgreSQL."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс моделей."""


class User(Base):
    """Пользователь Telegram."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    first_seen: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    surveys: Mapped[list["Survey"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Survey(Base):
    """Прохождение опроса."""

    __tablename__ = "surveys"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    answer_1: Mapped[str | None] = mapped_column(String)
    answer_2: Mapped[str | None] = mapped_column(String)
    answer_3: Mapped[str | None] = mapped_column(String)
    answer_4: Mapped[str | None] = mapped_column(String)
    answer_5: Mapped[str | None] = mapped_column(String)
    answer_6: Mapped[str | None] = mapped_column(String)
    answer_7: Mapped[str | None] = mapped_column(String)

    user: Mapped["User"] = relationship(back_populates="surveys")
