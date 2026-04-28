from sqlalchemy import select
from sqlalchemy.orm import Session

from app.hub import hub
from app.models import Notification
from app.rate_limiter import RateLimiter


def send_notification(db: Session, user_id: int, message: str, rate_limiter: RateLimiter) -> Notification:
    allowed = rate_limiter.allow(user_id)
    status = "delivered" if allowed else "rate_limited"

    notification = Notification(user_id=user_id, message=message, status=status)
    db.add(notification)
    db.commit()
    db.refresh(notification)

    if allowed:
        hub.publish(user_id, message)

    return notification


def list_notifications(db: Session, user_id: int, limit: int = 50) -> list[Notification]:
    return list(
        db.execute(
            select(Notification).where(Notification.user_id == user_id).order_by(Notification.id.desc()).limit(limit)
        ).scalars()
    )
