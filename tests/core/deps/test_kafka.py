from unittest.mock import Mock, patch

from src.core.deps.kafka import (
    Consumer,
    Producer,
    TestingConsumer,
    TestingProducer,
    get_consumer,
    get_producer,
)


def test_get_producer_testing():
    assert isinstance(get_producer({}), TestingProducer)


@patch("src.core.deps.kafka.confluent_kafka")
@patch("src.core.deps.kafka.Thread")
def test_get_producer_init(
    thread_mock, confluent_kafka_mock, override_settings
):
    confluent_kafka_mock.Producer.return_value = {
        "poll": "test_poll",
        "produce": Mock(),
    }

    with override_settings(APP_ENV="no-testing"):
        assert isinstance(get_producer({"prop": "value"}), Producer)

    confluent_kafka_mock.Producer.assert_called_once_with({"prop": "value"})

    assert confluent_kafka_mock.Producer.return_value["poll"] == "test_poll"
    assert confluent_kafka_mock.Producer.call_count == 1
    assert thread_mock.call_count == 1
    assert thread_mock.return_value.start.call_count == 1


@patch("src.core.deps.kafka.confluent_kafka")
@patch("src.core.deps.kafka.Thread")
def test_get_producer_produce(
    thread_mock, confluent_kafka_mock, override_settings
):
    confluent_kafka_mock.Producer.return_value = Mock()

    with override_settings(APP_ENV="no-testing"):
        producer = get_producer({})

    producer.produce("topic", "value", on_delivery="on_delivery")

    confluent_kafka_mock.Producer.return_value.produce.assert_called_once_with(
        "topic", "value", on_delivery="on_delivery", key=None
    )


@patch("src.core.deps.kafka.confluent_kafka")
@patch("src.core.deps.kafka.Thread")
def test_get_producer_close(
    thread_mock, confluent_kafka_mock, override_settings
):
    confluent_kafka_mock.Producer.return_value = Mock()

    with override_settings(APP_ENV="no-testing"):
        producer = get_producer({})

    producer.close()

    thread_mock.return_value.join.assert_called_once_with()


def test_get_consumer_testing():
    assert isinstance(get_consumer({}), TestingConsumer)


@patch("src.core.deps.kafka.confluent_kafka")
@patch("src.core.deps.kafka.Thread")
def test_get_consumer_init(
    thread_mock, confluent_kafka_mock, override_settings
):
    with override_settings(APP_ENV="no-testing"):
        assert isinstance(get_consumer({"prop": "value"}), Consumer)

    confluent_kafka_mock.Consumer.assert_called_once_with({"prop": "value"})

    assert confluent_kafka_mock.Consumer.call_count == 1
    assert thread_mock.call_count == 1


@patch("src.core.deps.kafka.confluent_kafka")
@patch("src.core.deps.kafka.Thread")
def test_get_consumer_start(
    thread_mock, confluent_kafka_mock, override_settings
):
    confluent_kafka_mock.Consumer.return_value = Mock()

    with override_settings(APP_ENV="no-testing"):
        consumer = get_consumer({})

    consumer.start()

    assert thread_mock.return_value.start.call_count == 1


@patch("src.core.deps.kafka.confluent_kafka")
@patch("src.core.deps.kafka.Thread")
def test_get_consumer_close(
    thread_mock, confluent_kafka_mock, override_settings
):
    confluent_kafka_mock.Producer.return_value = Mock()

    with override_settings(APP_ENV="no-testing"):
        consumer = get_consumer({})

    assert consumer._cancelled is False
    consumer.close()
    assert consumer._cancelled is True


@patch("src.core.deps.kafka.confluent_kafka")
@patch("src.core.deps.kafka.Thread")
def test_get_consumer_subscribe(
    thread_mock, confluent_kafka_mock, override_settings
):
    confluent_kafka_mock.Producer.return_value = Mock()

    with override_settings(APP_ENV="no-testing"):
        consumer = get_consumer({})

    assert consumer._topics_metadata == {}
    consumer.subscribe(
        [
            [
                "topic",
                "value",
                "callback",
            ]
        ]
    )
    assert consumer._topics_metadata == {
        "topic": {
            "message_class": "value",
            "on_message": "callback",
        }
    }
