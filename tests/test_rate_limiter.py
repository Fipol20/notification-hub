from app.rate_limiter import RateLimiter


def test_allows_requests_within_limit():
    limiter = RateLimiter(limit=3, window_seconds=60)
    assert limiter.allow(1, now=1000) is True
    assert limiter.allow(1, now=1001) is True
    assert limiter.allow(1, now=1002) is True


def test_blocks_after_limit_exceeded():
    limiter = RateLimiter(limit=2, window_seconds=60)
    assert limiter.allow(1, now=1000) is True
    assert limiter.allow(1, now=1001) is True
    assert limiter.allow(1, now=1002) is False


def test_limit_resets_after_window_slides():
    limiter = RateLimiter(limit=2, window_seconds=60)
    limiter.allow(1, now=1000)
    limiter.allow(1, now=1001)

    # через 61 секунду первые два хита уже выпали из окна
    assert limiter.allow(1, now=1062) is True


def test_limits_are_per_user():
    limiter = RateLimiter(limit=1, window_seconds=60)
    assert limiter.allow(1, now=1000) is True
    assert limiter.allow(1, now=1001) is False
    assert limiter.allow(2, now=1001) is True  # другой пользователь - свой лимит
