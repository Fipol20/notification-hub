"""
Скользящее окно на пользователя: не больше N уведомлений за последние
60 секунд. In-memory, не Redis - для одного инстанса это ок, при
горизонтальном масштабировании (несколько инстансов API) этот лимит
перестанет быть общим и его надо выносить в Redis/shared storage.
"""

import time
from collections import defaultdict, deque

from app.config import settings


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[int, deque[float]] = defaultdict(deque)

    def reset(self) -> None:
        self._hits.clear()

    def allow(self, user_id: int, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        hits = self._hits[user_id]

        cutoff = now - self.window_seconds
        while hits and hits[0] < cutoff:
            hits.popleft()

        if len(hits) >= self.limit:
            return False

        hits.append(now)
        return True


rate_limiter = RateLimiter(limit=settings.rate_limit_per_minute)
