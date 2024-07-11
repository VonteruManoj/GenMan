from unittest import mock

import pytest

from src.core.deps.slack import get_slack_service
from src.services.slack import FakeSlackService, SlackService

variations = [
    ("non-test", {}, FakeSlackService),
    ("non-test", {"channel_id": "channel_id"}, FakeSlackService),
    ("non-test", {"token": "token"}, FakeSlackService),
    ("non-test", {"channel_id": "channel_id", "token": "token"}, SlackService),
    ("testing", {}, FakeSlackService),
    ("testing", {"channel_id": "channel_id"}, FakeSlackService),
    ("testing", {"token": "token"}, FakeSlackService),
    (
        "testing",
        {"channel_id": "channel_id", "token": "token"},
        FakeSlackService,
    ),
]


@pytest.mark.parametrize(("env", "params", "result"), variations)
@mock.patch("src.services.slack.WebClient")
def test_get_slack_service(
    WebClient_mock, override_settings, env, params, result
):
    with override_settings(APP_ENV=env):
        assert isinstance(get_slack_service(**params), result)
    get_slack_service.cache_clear()
