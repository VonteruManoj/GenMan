from threading import Thread

import confluent_kafka

from src.contracts.events import EventProducerInterface
from src.core.config import get_settings
from src.core.deps.logger import with_logger


def get_producer(configs):
    if get_settings().APP_ENV == "testing":
        return TestingProducer(configs)
    return Producer(configs)


def get_consumer(configs):
    if get_settings().APP_ENV == "testing":
        return TestingConsumer(configs)
    return Consumer(configs)


@with_logger()
class TestingProducer:
    def __init__(self, configs):
        self._logger.info("TestingProducer initialized")

    def close(self):
        self._logger.info("Closing TestingProducer")

    def produce(self, topic, value, on_delivery=None):
        self._logger.info(f"Producing msg on `{topic}`")


class Producer(EventProducerInterface):
    def __init__(self, configs):
        self._producer = confluent_kafka.Producer(configs)
        self._cancelled = False
        self._poll_thread = Thread(target=self._poll_loop)
        self._poll_thread.start()

    def _poll_loop(self):
        while not self._cancelled:
            self._producer.poll(0.1)

    def close(self):
        self._cancelled = True
        self._poll_thread.join()

    def produce(self, topic, value, on_delivery=None, key=None):
        self._producer.produce(topic, value, on_delivery=on_delivery, key=key)


@with_logger()
class TestingConsumer:
    def __init__(self, configs):
        self._logger.info("TestingConsumer initialized")

    def start(self):
        self._logger.info("Starting TestingConsumer")

    def close(self):
        self._logger.info("Closing TestingConsumer")

    def subscribe(self, topics):
        self._logger.info("Subscribing to topics")


@with_logger()
class Consumer:
    def __init__(self, configs):
        self._consumer = confluent_kafka.Consumer(configs)
        self._cancelled = False
        self._poll_thread = Thread(target=self._poll_loop)
        self._topics_metadata = {}

    def _poll_loop(self):
        try:
            while not self._cancelled:
                msg = self._consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    if (
                        msg.error().code()
                        == confluent_kafka.KafkaError._PARTITION_EOF
                    ):
                        self._logger.warning(
                            "Kafka consumer reached end of partition"
                        )
                        continue
                    else:
                        self._logger.error(
                            f"Kafka consumer error: {msg.error()}"
                        )
                        break

                # Process Kafka messages here
                topic = msg.topic()
                if topic in self._topics_metadata:
                    payload = self._topics_metadata[topic]["message_class"]()
                    payload.ParseFromString(msg.value())
                    self._topics_metadata[topic]["on_message"](payload)
                else:
                    self._logger.warning(
                        "Kafka consumer received message on "
                        f"unknown topic: {topic}"
                    )
        finally:
            self._consumer.close()

    def start(self):
        self._poll_thread.start()

    def close(self):
        self._cancelled = True

    def subscribe(self, topics):
        self._consumer.subscribe([topic[0] for topic in topics])
        for topic in topics:
            self._topics_metadata[topic[0]] = {
                "message_class": topic[1],
                "on_message": topic[2],
            }
