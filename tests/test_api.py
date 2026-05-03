def test_create_user_and_send_notification(client):
    user = client.post("/users", json={"username": "vasya"}).json()

    resp = client.post(f"/users/{user['id']}/notifications", json={"message": "привет"})
    assert resp.status_code == 201
    assert resp.json()["status"] == "delivered"

    history = client.get(f"/users/{user['id']}/notifications").json()
    assert len(history) == 1
    assert history[0]["message"] == "привет"


def test_duplicate_username_returns_409(client):
    client.post("/users", json={"username": "vasya"})
    resp = client.post("/users", json={"username": "vasya"})
    assert resp.status_code == 409


def test_notify_unknown_user_returns_404(client):
    resp = client.post("/users/9999/notifications", json={"message": "привет"})
    assert resp.status_code == 404


def test_rate_limit_returns_429(client, monkeypatch):
    from app.rate_limiter import rate_limiter

    rate_limiter.reset()
    monkeypatch.setattr(rate_limiter, "limit", 1)

    user = client.post("/users", json={"username": "petya"}).json()

    first = client.post(f"/users/{user['id']}/notifications", json={"message": "первое"})
    assert first.status_code == 201

    second = client.post(f"/users/{user['id']}/notifications", json={"message": "второе"})
    assert second.status_code == 429
