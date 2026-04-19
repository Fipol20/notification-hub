import datetime as dt

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(), default=utcnow)


class Notification(Base):
    """История уведомлений. Доставка в realtime (SSE) - отдельно, в hub.py,
    а тут хранится то, что уже было отправлено (или отклонено рейт-лимитом),
    чтобы пользователь мог посмотреть историю, даже если был оффлайн."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(Text)
    # delivered | rate_limited
    status: Mapped[str] = mapped_column(String(20), default="delivered")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(), default=utcnow)
