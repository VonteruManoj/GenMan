from unittest import mock

import pytest

from src.adapters.ai_api import FakeOpenAIClient, OpenAIClient
from src.core.deps.ai_client import get_open_ai_client

variations = [
    ("production", {}, OpenAIClient),
    ("production", {"org_id": "org_id"}, OpenAIClient),
    ("production", {"api_key": "api_key"}, OpenAIClient),
    ("production", {"org_id": "org_id", "api_key": "api_key"}, OpenAIClient),
    ("testing", {}, FakeOpenAIClient),
    ("testing", {"org_id": "org_id"}, FakeOpenAIClient),
    ("testing", {"api_key": "api_key"}, FakeOpenAIClient),
    ("testing", {"org_id": "org_id", "api_key": "api_key"}, FakeOpenAIClient),
    ("local", {}, FakeOpenAIClient),
    ("local", {"org_id": "org_id"}, FakeOpenAIClient),
    ("local", {"api_key": "api_key"}, FakeOpenAIClient),
    ("local", {"org_id": "org_id", "api_key": "api_key"}, OpenAIClient),
]


@pytest.mark.parametrize(("env", "params", "result"), variations)
@mock.patch("src.adapters.ai_api.openai")
def test_get_open_ai_client(
    openai_mock, override_settings, env, params, result, check_log_message
):
    with override_settings(APP_ENV=env):
        is_fake_text = "FAKE - " if result == FakeOpenAIClient else ""
        assert isinstance(get_open_ai_client(**params), result)

        check_log_message(
            "DEBUG", f"[{is_fake_text}OpenAI] Creating client..."
        )

    get_open_ai_client.cache_clear()
