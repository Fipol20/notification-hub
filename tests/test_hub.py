import pytest

from app.hub import NotificationHub


@pytest.mark.asyncio
async def test_publish_delivers_to_subscriber():
    hub = NotificationHub()
    queue = hub.subscribe(user_id=1)

    delivered = hub.publish(1, "привет")

    assert delivered == 1
    assert queue.get_nowait() == "привет"


def test_publish_to_user_without_subscribers_delivers_nothing():
    hub = NotificationHub()
    assert hub.publish(999, "никому") == 0


def test_unsubscribe_stops_delivery():
    hub = NotificationHub()
    queue = hub.subscribe(user_id=1)
    hub.unsubscribe(1, queue)

    assert hub.publish(1, "уже отписался") == 0


def test_backpressure_drops_messages_when_queue_is_full():
    hub = NotificationHub(max_queue_size=2)
    hub.subscribe(user_id=1)

    assert hub.publish(1, "первое") == 1
    assert hub.publish(1, "второе") == 1
    # очередь переполнена - сообщение отбрасывается, а не блокирует отправителя
    assert hub.publish(1, "третье, не влезло") == 0


def test_multiple_subscribers_all_receive_message():
    hub = NotificationHub()
    hub.subscribe(user_id=1)
    hub.subscribe(user_id=1)

    assert hub.subscriber_count(1) == 2
    assert hub.publish(1, "всем") == 2
