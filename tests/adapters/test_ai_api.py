import json
from unittest import mock
from unittest.mock import patch

import pytest

from src.adapters.ai_api import FakeOpenAIClient, OpenAIClient
from src.chain.chain import ChainId
from src.exceptions.ai_api import AIApiResponseFormatException
from src.repositories.models.usage_log_repository import UsageLogRepository


# ----------------------------------------------
# OpenAIClient
# ----------------------------------------------
@patch("src.adapters.ai_api.openai")
def test_api_key_and_org_id_are_set_on_init(openai_mock, check_log_message):
    usage_log_repository_mock = mock.Mock(spec=UsageLogRepository)
    OpenAIClient(
        "testing-openai-org-id",
        "testing-openai-api-key",
        usage_log_repository_mock,
    )

    assert openai_mock.organization == "testing-openai-org-id"
    assert openai_mock.api_key == "testing-openai-api-key"

    check_log_message("INFO", "OpenAI API client initialized")


@patch("src.adapters.ai_api.openai")
def test_calls_openai_completion(openai_mock, check_log_message):
    usage_log_repository_mock = mock.Mock(spec=UsageLogRepository)
    configs = {
        "model": "davinci",
        "temperature": 0.9,
        "top_p": 1.0,
    }
    completion_response = {"choices": [{"text": "This is a test response"}]}
    openai_mock.Completion.create.return_value = completion_response

    client = OpenAIClient(
        "testing-openai-org-id",
        "testing-openai-api-key",
        usage_log_repository_mock,
    )

    chain_id = ChainId("testing-chain-operation")
    client.set_chain_id(chain_id)

    response = client.completion(
        prompt="This is a test",
        original_text="This is a test",
        operation="do-ai-stuff",
        configs=configs,
    )

    args = {
        "model": "davinci",
        "temperature": 0.9,
        "top_p": 1.0,
        "prompt": "This is a test",
    }
    openai_mock.Completion.create.assert_called_with(**args)

    assert response == "This is a test response"
    usage_log_repository_mock.create.assert_called_once_with(
        operation="do-ai-stuff",
        prompt=json.dumps("This is a test"),
        input=json.dumps("This is a test"),
        response=json.dumps(completion_response),
        output=json.dumps("This is a test response"),
        chain_id=chain_id.id,
        chain_operation=chain_id.operation,
    )

    check_log_message(
        "INFO", f"OpenAI API completion called with: {json.dumps(args)}"
    )


@patch("src.adapters.ai_api.openai")
def test_completion_without_choices_return_empty_string_and_logs(
    openai_mock, check_log_message
):
    usage_log_repository_mock = mock.Mock(spec=UsageLogRepository)
    configs = {
        "model": "davinci",
        "temperature": 0.9,
        "top_p": 1.0,
    }
    openai_mock.Completion.create.return_value = {"choices": []}

    client = OpenAIClient(
        "testing-openai-org-id",
        "testing-openai-api-key",
        usage_log_repository_mock,
    )
    client = OpenAIClient(
        "testing-openai-org-id",
        "testing-openai-api-key",
        usage_log_repository_mock,
    )

    with pytest.raises(AIApiResponseFormatException):
        client.completion(
            prompt="This is a test",
            original_text="This is a test",
            operation="do-ai-stuff",
            configs=configs,
        )

    openai_mock.Completion.create.assert_called_with(
        prompt="This is a test", model="davinci", temperature=0.9, top_p=1.0
    )

    check_log_message(
        "WARNING",
        "OpenAI API completion response"
        ' without choices, prompt: "This is a test"',
    )


@patch("src.adapters.ai_api.openai")
def test_openai_completion_choice_is_trimm(openai_mock):
    usage_log_repository_mock = mock.Mock(spec=UsageLogRepository)
    configs = {
        "model": "davinci",
        "temperature": 0.9,
        "top_p": 1.0,
    }
    openai_mock.Completion.create.return_value = {
        "choices": [{"text": "\nThis is a test response "}]
    }

    client = OpenAIClient(
        "testing-openai-org-id",
        "testing-openai-api-key",
        usage_log_repository_mock,
    )

    chain_id = ChainId("testing-chain-operation")
    client.set_chain_id(chain_id)

    response = client.completion(
        prompt="This is a test",
        original_text="This is a test",
        operation="do-ai-stuff",
        configs=configs,
    )

    openai_mock.Completion.create.assert_called_with(
        prompt="This is a test", model="davinci", temperature=0.9, top_p=1.0
    )

    assert response == "This is a test response"
    usage_log_repository_mock.create.assert_called_once()


@patch("src.adapters.ai_api.openai")
def test_calls_openai_chat_completion(
    openai_mock, make_chat_completion_prompt_plain, check_log_message
):
    usage_log_repository_mock = mock.Mock(spec=UsageLogRepository)
    configs = {
        "model": "davinci",
        "temperature": 0.9,
        "top_p": 1.0,
    }

    chat_completion_response = {
        "choices": [{"message": {"content": "This is a test response"}}]
    }

    openai_mock.ChatCompletion.create.return_value = chat_completion_response

    client = OpenAIClient(
        "testing-openai-org-id",
        "testing-openai-api-key",
        usage_log_repository_mock,
    )

    chain_id = ChainId("testing-chain-operation")
    client.set_chain_id(chain_id)

    response = client.chat_completion(
        messages=make_chat_completion_prompt_plain()["messages"],
        original_text="This is a test",
        operation="do-ai-stuff",
        configs=configs,
    )

    args = {
        "model": "davinci",
        "temperature": 0.9,
        "top_p": 1.0,
        "messages": make_chat_completion_prompt_plain()["messages"],
    }
    openai_mock.ChatCompletion.create.assert_called_with(**args)

    assert response == "This is a test response"
    usage_log_repository_mock.create.assert_called_once_with(
        operation="do-ai-stuff",
        prompt=json.dumps(make_chat_completion_prompt_plain()["messages"]),
        input=json.dumps("This is a test"),
        response=json.dumps(chat_completion_response),
        output=json.dumps("This is a test response"),
        chain_id=chain_id.id,
        chain_operation=chain_id.operation,
    )

    check_log_message(
        "INFO",
        f"OpenAI API chat completion called with: {json.dumps(args)}",
    )


@patch("src.adapters.ai_api.openai")
def test_chat_completion_without_choices_return_empty_string_and_logs(
    openai_mock, check_log_message, make_chat_completion_prompt_plain
):
    usage_log_repository_mock = mock.Mock(spec=UsageLogRepository)
    configs = {
        "model": "davinci",
        "temperature": 0.9,
        "top_p": 1.0,
    }
    openai_mock.ChatCompletion.create.return_value = {"choices": []}

    client = OpenAIClient(
        "testing-openai-org-id",
        "testing-openai-api-key",
        usage_log_repository_mock,
    )

    with pytest.raises(AIApiResponseFormatException):
        client.chat_completion(
            make_chat_completion_prompt_plain()["messages"],
            "This is a test",
            "do-ai-stuff",
            configs,
        )

    openai_mock.ChatCompletion.create.assert_called_with(
        messages=make_chat_completion_prompt_plain()["messages"],
        model="davinci",
        temperature=0.9,
        top_p=1.0,
    )

    check_log_message(
        "WARNING",
        "OpenAI API chat completion response without choices, messages: "
        f'{json.dumps(make_chat_completion_prompt_plain()["messages"])}',
    )


@patch("src.adapters.ai_api.openai")
def test_openai_chat_completion_choice_is_trimm(
    openai_mock, make_chat_completion_prompt_plain
):
    usage_log_repository_mock = mock.Mock(spec=UsageLogRepository)
    configs = {
        "model": "davinci",
        "temperature": 0.9,
        "top_p": 1.0,
    }
    openai_mock.ChatCompletion.create.return_value = {
        "choices": [{"message": {"content": "\nThis is a test response  "}}]
    }

    client = OpenAIClient(
        "testing-openai-org-id",
        "testing-openai-api-key",
        usage_log_repository_mock,
    )
    chain_id = ChainId("testing-chain-operation")
    client.set_chain_id(chain_id)

    response = client.chat_completion(
        make_chat_completion_prompt_plain()["messages"],
        "This is a test",
        "do-ai-stuff",
        configs,
    )

    openai_mock.ChatCompletion.create.assert_called_with(
        messages=make_chat_completion_prompt_plain()["messages"],
        model="davinci",
        temperature=0.9,
        top_p=1.0,
    )

    assert response == "This is a test response"
    usage_log_repository_mock.create.assert_called_once()


@patch("src.adapters.ai_api.openai")
def test_openai_moderation(openai_mock, check_log_message):
    usage_log_repository_mock = mock.Mock(spec=UsageLogRepository)
    moderation_response = {"results": [{"flagged": True}]}
    openai_mock.Moderation.create.return_value = moderation_response

    client = OpenAIClient(
        "testing-openai-org-id",
        "testing-openai-api-key",
        usage_log_repository_mock,
    )
    chain_id = ChainId("testing-chain-operation")
    client.set_chain_id(chain_id)
    response = client.moderation("This is a test", "moderation")

    openai_mock.Moderation.create.assert_called_with("This is a test")

    assert response is True
    usage_log_repository_mock.create.assert_called_once_with(
        operation="moderation",
        prompt=json.dumps("This is a test"),
        input=json.dumps("This is a test"),
        response=json.dumps(moderation_response),
        output=json.dumps(True),
        chain_id=chain_id.id,
        chain_operation=chain_id.operation,
    )

    args = {"input": "This is a test", "operation": "moderation"}

    check_log_message(
        "INFO",
        f"OpenAI API moderation called with: {json.dumps(args)}",
    )


@patch("src.adapters.ai_api.openai")
def test_openai_moderation_fails(openai_mock, check_log_message):
    usage_log_repository_mock = mock.Mock(spec=UsageLogRepository)
    openai_mock.Moderation.create.return_value = {}

    client = OpenAIClient(
        "testing-openai-org-id",
        "testing-openai-api-key",
        usage_log_repository_mock,
    )

    with pytest.raises(AIApiResponseFormatException):
        client.moderation("This is a test", "moderation")

    openai_mock.Moderation.create.assert_called_with("This is a test")

    check_log_message(
        "WARNING",
        "OpenAI API invalid moderation" ' response, input: "This is a test"',
    )


# ----------------------------------------------
# FakeOpenAIClient
# ----------------------------------------------
def test_fake_openai_completion():
    usage_log_repository_mock = mock.Mock(spec=UsageLogRepository)
    client = FakeOpenAIClient(usage_log_repository_mock)
    chain_id = ChainId("testing-chain-operation")
    client.set_chain_id(chain_id)

    response = client.completion(
        "This is a test", "This is a test", "do-ai-stuff", {}
    )

    assert response == (
        "This is a completion fake response, prompt: This is a test"
    )
    usage_log_repository_mock.create.assert_called_once_with(
        operation="do-ai-stuff",
        prompt=json.dumps("Local call"),
        input=json.dumps("This is a test"),
        response=json.dumps("Local call"),
        output=json.dumps(
            "This is a completion fake response, prompt: This is a test"
        ),
        chain_id=chain_id.id,
        chain_operation=chain_id.operation,
    )


def test_fake_openai_chat_completion(make_chat_completion_prompt_plain):
    usage_log_repository_mock = mock.Mock(spec=UsageLogRepository)
    client = FakeOpenAIClient(usage_log_repository_mock)
    chain_id = ChainId("testing-chain-operation")
    client.set_chain_id(chain_id)

    response = client.chat_completion(
        make_chat_completion_prompt_plain()["messages"],
        "This is a test",
        "do-ai-stuff",
        {},
    )

    assert "This is a chat completion fake response" in response
    assert "Shorten the text:" in response

    expected_output = json.dumps(
        "This is a chat completion fake response, messages: %s"
        % json.dumps(make_chat_completion_prompt_plain()["messages"])
    )

    usage_log_repository_mock.create.assert_called_once_with(
        operation="do-ai-stuff",
        prompt=json.dumps("Local call"),
        input=json.dumps("This is a test"),
        response=json.dumps("Local call"),
        output=expected_output,
        chain_id=chain_id.id,
        chain_operation=chain_id.operation,
    )


def test_fake_openai_moderation_returns_false():
    usage_log_repository_mock = mock.Mock(spec=UsageLogRepository)
    client = FakeOpenAIClient(usage_log_repository_mock)
    chain_id = ChainId("testing-chain-operation")
    client.set_chain_id(chain_id)

    response = client.moderation("Text to be moderated", "moderation")

    assert response is False
    usage_log_repository_mock.create.assert_called_once_with(
        operation="moderation",
        prompt=json.dumps("Local call"),
        input=json.dumps("Text to be moderated"),
        response=json.dumps("Local call"),
        output=json.dumps(False),
        chain_id=chain_id.id,
        chain_operation=chain_id.operation,
    )
