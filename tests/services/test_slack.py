from unittest.mock import patch

from src.services.slack import (
    FakeSlackService,
    SlackService,
    prepare_function_log_message,
)


# ----------------------------------------------
# SlackService
# ----------------------------------------------
def test_prepare_function_log_message():
    assert prepare_function_log_message("test", "input", "output") == (
        "*Function:* test\n*Input:* input\n*Output:* output\n"
    )


# ----------------------------------------------
# SlackService
# ----------------------------------------------
@patch("src.services.slack.WebClient.chat_postMessage")
def test_slack_service_send_message(chat_postMessage_mock, check_log_message):
    service = SlackService("test_id", "test_token")
    chat_postMessage_mock.return_value = None
    service.send_message("Hello world!")

    chat_postMessage_mock.assert_called_with(
        channel="test_id",
        text="Hello world!",
    )

    check_log_message(
        "INFO",
        "Slack message sent to channel: test_id",
    )


@patch("src.services.slack.WebClient.chat_postMessage")
def test_slack_service_send_message_fails(
    chat_postMessage_mock, check_log_message
):
    chat_postMessage_mock.side_effect = Exception("test error")
    service = SlackService("test_id", "test_token")
    service.send_message("Hello world!")

    check_log_message(
        "WARNING",
        "Error [test error] sending Slack message to channel: test_id",
    )


@patch("src.services.slack.SlackService.send_message")
def test_slack_service_send_fn_log(send_message_mock):
    send_message_mock.return_value = None
    service = SlackService("test_id", "test_token")
    service.send_function_log_message("test", "input", "output")

    send_message_mock.assert_called_with(
        "*Function:* test\n*Input:* input\n*Output:* output\n"
    )


# ----------------------------------------------
# FakeSlackService
# ----------------------------------------------
def test_fake_slack_service_send_message(check_log_message):
    service = FakeSlackService()
    service.send_message("Hello world!")

    check_log_message(
        "INFO",
        '[FAKE] Slack message "Hello world!" sent.',
    )


@patch("src.services.slack.FakeSlackService.send_message")
def test_fake_slack_service_send_fn_log(send_message_mock):
    send_message_mock.return_value = None
    service = FakeSlackService()
    service.send_function_log_message("test", "input", "output")

    send_message_mock.assert_called_with(
        "*Function:* test\n*Input:* input\n*Output:* output\n"
    )
