# notification-hub

Уведомление пишется в базу и сразу уходит в открытые SSE-соединения этого пользователя. Вкладок может быть несколько: у каждой своя очередь.

```bash
docker compose up --build
```

http://localhost:8000/docs

Без Docker:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Терминал 1:

```bash
curl -N localhost:8000/users/1/stream
```

Терминал 2:

```bash
curl -X POST localhost:8000/users -H "Content-Type: application/json" -d '{"username": "vasya"}'
curl -X POST localhost:8000/users/1/notifications \
  -H "Content-Type: application/json" -d '{"message": "привет из второго терминала"}'
```

Очередь соединения — 50 сообщений. Дальше новые для зависшей вкладки отбрасываются, `POST` из-за этого не блокируется. Если слать чаще `RATE_LIMIT_PER_MINUTE` (30), API ответит 429.

Лимит и список подписчиков в памяти процесса. Рестарт их забывает, строки в Postgres остаются. История: `GET /users/1/notifications`. Авторизации нет, поток открывается по `user_id`.

Пока тишина, раз в 15 секунд в поток пишется heartbeat.

```bash
pytest -v
```
