import asyncio

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.hub import hub
from app.models import User
from app.notification_service import list_notifications, send_notification
from app.rate_limiter import rate_limiter
from app.schemas import NotificationCreate, NotificationOut

router = APIRouter(tags=["notifications"])


@router.post("/users/{user_id}/notifications", response_model=NotificationOut, status_code=201)
def notify_user(user_id: int, payload: NotificationCreate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "пользователь не найден")

    notification = send_notification(db, user_id, payload.message, rate_limiter)
    if notification.status == "rate_limited":
        raise HTTPException(429, "превышен лимит уведомлений для этого пользователя")
    return notification


@router.get("/users/{user_id}/notifications", response_model=list[NotificationOut])
def history(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "пользователь не найден")
    return list_notifications(db, user_id)


@router.get("/users/{user_id}/stream")
async def stream(user_id: int):
    """SSE-поток уведомлений для пользователя. Открыть в браузере/curl:
    curl -N localhost:8000/users/1/stream"""
    queue = hub.subscribe(user_id)

    async def event_generator():
        try:
            while True:
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=15)
                    yield f"data: {message}\n\n"
                except asyncio.TimeoutError:
                    # heartbeat, чтобы соединение не отваливалось по таймауту
                    # у прокси/браузера, пока нет реальных уведомлений
                    yield ": heartbeat\n\n"
        finally:
            hub.unsubscribe(user_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
