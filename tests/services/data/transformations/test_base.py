from unittest.mock import ANY, Mock

from src.services.data.transformations.base import BaseService


def test_set_notifier_data():
    s = BaseService(None, None)

    s._set_notifier_data(
        "doc_id",
        1,
        2,
    )

    assert s._notifier_data == {
        "start": ANY,
        "doc_id": "doc_id",
        "org_id": 1,
        "connector_id": 2,
    }


def test_notify_skip_without_notifier(check_log_message):
    s = BaseService(None, None)

    s._set_notifier_data(
        "doc_id",
        1,
        2,
    )

    s._notify(
        8,
        4,
        "reason",
    )

    check_log_message(
        "ERROR",
        "No event producer configured, skipping notification for job status",
    )


def test_notify():
    s = BaseService(None, Mock())

    s._set_notifier_data(
        "doc_id",
        1,
        2,
    )

    s.set_job_id("TheID12")

    s._notify(
        1,
        4,
        "reason",
    )

    # TODO: due to duration we need to mokey
    # patch time.time() to return stable value
    # example: b"\n\x06doc_id\x10\x01\x18\x02(\x010\x04:\x06reasonB\x07TheID12", # noqa: E501
    s._event_producer.produce.assert_called_once_with(
        "embed-job-status-local-test", ANY, key="TheID12"
    )
