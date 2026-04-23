"""
In-memory pub/sub: fan-out уведомления всем открытым SSE-соединениям
пользователя (их может быть несколько - разные вкладки/устройства).

Очередь на соединение ограничена (maxsize) - это и есть backpressure:
если клиент не успевает читать (медленная сеть, зависшая вкладка),
новые уведомления для него отбрасываются, а не копят память бесконечно.
Для одного процесса этого хватает; для нескольких инстансов API это
надо заменить на Redis pub/sub, иначе уведомление дойдёт только до того
инстанса, к которому подключён клиент.
"""

import asyncio
from collections import defaultdict


class NotificationHub:
    def __init__(self, max_queue_size: int = 50):
        self.max_queue_size = max_queue_size
        self._subscribers: dict[int, set[asyncio.Queue]] = defaultdict(set)

    def subscribe(self, user_id: int) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=self.max_queue_size)
        self._subscribers[user_id].add(queue)
        return queue

    def unsubscribe(self, user_id: int, queue: asyncio.Queue) -> None:
        subscribers = self._subscribers.get(user_id)
        if not subscribers:
            return
        subscribers.discard(queue)
        if not subscribers:
            del self._subscribers[user_id]

    def publish(self, user_id: int, message: str) -> int:
        """Возвращает, скольким соединениям удалось доставить сообщение
        (без учёта отброшенных из-за переполнения очереди)."""
        delivered = 0
        for queue in list(self._subscribers.get(user_id, [])):
            try:
                queue.put_nowait(message)
                delivered += 1
            except asyncio.QueueFull:
                # клиент не успевает читать - пропускаем, не блокируемся
                continue
        return delivered

    def subscriber_count(self, user_id: int) -> int:
        return len(self._subscribers.get(user_id, []))


hub = NotificationHub()
