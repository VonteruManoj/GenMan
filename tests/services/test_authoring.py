from unittest.mock import Mock, patch

from src.schemas.assets.prompts import CompletionPrompt, PromptTemplates
from src.services.authoring import (
    AuthoringService,
    ChangeToneService,
    ExpandWritingService,
    FixGrammarAuthoringService,
    ImproveWritingService,
    ReduceReadingComplexityService,
    ReduceReadingTimeService,
    SummarizeIntoStepsService,
    SummarizeService,
    TranslateService,
)
from src.services.slack import FakeSlackService


# ----------------------------------------------
# AuthoringService
# ----------------------------------------------
@patch("src.services.authoring.AuthoringService.__abstractmethods__", set())
def test_service_load_templates_at_init(
    make_prompt_templates_plain, check_log_message
):
    ai_api_mock = Mock()
    assets_repo_mock = Mock()
    assets_repo_mock.get_json_asset.return_value = (
        make_prompt_templates_plain()
    )
    assets_filename = "assets_filename.json"

    service = AuthoringService(
        ai_api_mock, assets_repo_mock, assets_filename, FakeSlackService()
    )

    assets_repo_mock.get_json_asset.assert_called_with(assets_filename)
    assert isinstance(service.templates, PromptTemplates)
    assert isinstance(service.templates.FixGrammar, CompletionPrompt)
    check_log_message(
        "DEBUG", f"[Authoring] Loading template configs: {assets_filename}"
    )
    check_log_message(
        "DEBUG", f"[Authoring] Loaded template configs: {assets_filename}"
    )


# ----------------------------------------------
# FixGrammarAuthoringService
# ----------------------------------------------
def test_fix_grammar(
    make_prompt_templates_plain,
    make_completion_prompt_plain,
    check_log_message,
):
    ai_api_mock = Mock()
    ai_api_mock.completion.return_value = "This is a test"
    assets_repo_mock = Mock()
    assets_repo_mock.get_json_asset.return_value = (
        make_prompt_templates_plain()
    )
    assets_filename = "assets_filename.json"
    slack_service_mock = Mock()

    # Build prompt service
    text = "This is a test"
    service = FixGrammarAuthoringService(
        ai_api_mock, assets_repo_mock, assets_filename, slack_service_mock
    )
    service.handle(text)

    # Check prompt service
    ai_api_mock.completion.assert_called_with(
        make_completion_prompt_plain()["prompt"].replace("{{text}}", text),
        text,
        "fix-grammar",
        {
            "model": "davinci",
            "temperature": 0.5,
            "top_p": 0.8,
            "max_tokens": 160,
        },
    )

    # Check slack message
    slack_service_mock.send_function_log_message.assert_called_with(
        "Fix Grammar", text, "This is a test"
    )

    check_log_message("INFO", "[Authoring] Executing Fix Grammar prompt...")
    check_log_message("INFO", "[Authoring] Executed Fix Grammar prompt")


# ----------------------------------------------
# SummarizeService
# ----------------------------------------------
def test_summarize(
    make_prompt_templates_plain,
    make_chat_completion_prompt_plain,
    check_log_message,
):
    ai_api_mock = Mock()
    ai_api_mock.chat_completion.return_value = (
        "This is a test - Chat Completion"
    )
    assets_repo_mock = Mock()
    assets_repo_mock.get_json_asset.return_value = (
        make_prompt_templates_plain()
    )
    assets_filename = "assets_filename.json"
    slack_service_mock = Mock()

    # Build prompt service
    text = "This is a test"
    service = SummarizeService(
        ai_api_mock, assets_repo_mock, assets_filename, slack_service_mock
    )
    service.handle(text)

    expected_messages = make_chat_completion_prompt_plain()["messages"]
    expected_messages[1]["content"] = expected_messages[1]["content"].replace(
        "{{text}}", text
    )

    # Check prompt service
    ai_api_mock.chat_completion.assert_called_with(
        expected_messages,
        text,
        "summarize",
        {
            "model": "davinci",
            "temperature": 0.5,
            "top_p": 0.8,
            "max_tokens": 160,
        },
    )

    # Check slack message
    slack_service_mock.send_function_log_message.assert_called_with(
        "Summarize", text, "This is a test - Chat Completion"
    )

    check_log_message("INFO", "[Authoring] Executing Summarize prompt...")
    check_log_message("INFO", "[Authoring] Executed Summarize prompt")


# ----------------------------------------------
# SummarizeIntoStepsService
# ----------------------------------------------
def test_summarize_into_steps(
    make_prompt_templates_plain,
    make_chat_completion_prompt_plain,
    check_log_message,
):
    ai_api_mock = Mock()
    ai_api_mock.chat_completion.return_value = (
        "This is a test - Chat Completion"
    )
    assets_repo_mock = Mock()
    assets_repo_mock.get_json_asset.return_value = (
        make_prompt_templates_plain()
    )
    assets_filename = "assets_filename.json"
    slack_service_mock = Mock()

    # Build prompt service
    text = "This is a test"
    service = SummarizeIntoStepsService(
        ai_api_mock, assets_repo_mock, assets_filename, slack_service_mock
    )
    service.handle(text)

    expected_messages = make_chat_completion_prompt_plain()["messages"]
    expected_messages[1]["content"] = expected_messages[1]["content"].replace(
        "{{text}}", text
    )

    # Check prompt service
    ai_api_mock.chat_completion.assert_called_with(
        expected_messages,
        text,
        "summarize-into-steps",
        {
            "model": "davinci",
            "temperature": 0.5,
            "top_p": 0.8,
            "max_tokens": 160,
        },
    )

    # Check slack message
    slack_service_mock.send_function_log_message.assert_called_with(
        "Summarize Into Steps", text, "This is a test - Chat Completion"
    )

    check_log_message(
        "INFO", "[Authoring] Executing Summarize Into Steps prompt..."
    )
    check_log_message(
        "INFO", "[Authoring] Executed Summarize Into Steps prompt"
    )


# ----------------------------------------------
# ChangeToneService
# ----------------------------------------------
def test_change_tone(make_prompt_templates_plain, check_log_message):
    ai_api_mock = Mock()
    ai_api_mock.chat_completion.return_value = (
        "This is a test - Chat Completion"
    )
    assets_repo_mock = Mock()
    assets_repo_mock.get_json_asset.return_value = (
        make_prompt_templates_plain()
    )
    assets_filename = "assets_filename.json"
    slack_service_mock = Mock()

    # Build prompt service
    text = "This is a test"
    tone = "friendly"
    service = ChangeToneService(
        ai_api_mock, assets_repo_mock, assets_filename, slack_service_mock
    )
    service.handle(text, tone)

    expected_messages = make_prompt_templates_plain()["ChangeTone"]["messages"]
    expected_messages[1]["content"] = "Change to %s:\n\n%s" % (tone, text)

    # Check prompt service
    ai_api_mock.chat_completion.assert_called_with(
        expected_messages,
        text,
        "change-tone",
        {
            "model": "davinci",
            "temperature": 0.5,
            "top_p": 0.8,
            "max_tokens": 160,
        },
    )

    # Check slack message
    slack_service_mock.send_function_log_message.assert_called_with(
        f"Change Tone [{tone}]", text, "This is a test - Chat Completion"
    )

    check_log_message(
        "INFO", f"[Authoring] Executing Change Tone [{tone}] prompt..."
    )
    check_log_message(
        "INFO", f"[Authoring] Executed Change Tone [{tone}] prompt"
    )


# ----------------------------------------------
# TranslateService
# ----------------------------------------------
def test_translate(make_prompt_templates_plain, check_log_message):
    ai_api_mock = Mock()
    ai_api_mock.chat_completion.return_value = "Esto es una prueba"
    assets_repo_mock = Mock()
    assets_repo_mock.get_json_asset.return_value = (
        make_prompt_templates_plain()
    )
    assets_filename = "assets_filename.json"
    slack_service_mock = Mock()

    # Build prompt service
    text = "This is a test"
    language = "spanish"
    service = TranslateService(
        ai_api_mock, assets_repo_mock, assets_filename, slack_service_mock
    )
    service.handle(text, language)

    expected_messages = make_prompt_templates_plain()["Translate"]["messages"]
    expected_messages[1]["content"] = "Translate to %s:\n\n%s" % (
        language,
        text,
    )

    # Check prompt service
    ai_api_mock.chat_completion.assert_called_with(
        expected_messages,
        text,
        "translate",
        {
            "model": "davinci",
            "temperature": 0.5,
            "top_p": 0.8,
            "max_tokens": 160,
        },
    )

    # Check slack message
    slack_service_mock.send_function_log_message.assert_called_with(
        f"Translate [to: {language}]",
        text,
        "Esto es una prueba",
    )

    check_log_message(
        "INFO", f"[Authoring] Executing Translate [to: {language}] prompt..."
    )
    check_log_message(
        "INFO", f"[Authoring] Executed Translate [to: {language}] prompt"
    )


# ----------------------------------------------
# ImproveWritingService
# ----------------------------------------------
def test_improve_writing(make_prompt_templates_plain, check_log_message):
    ai_api_mock = Mock()
    ai_api_mock.chat_completion.return_value = "Jon's text"
    assets_repo_mock = Mock()
    assets_repo_mock.get_json_asset.return_value = (
        make_prompt_templates_plain()
    )
    assets_filename = "assets_filename.json"
    slack_service_mock = Mock()

    # Build prompt service
    text = "This is the text of Jon"
    service = ImproveWritingService(
        ai_api_mock, assets_repo_mock, assets_filename, slack_service_mock
    )
    service.handle(text)

    expected_messages = make_prompt_templates_plain()["ImproveWriting"][
        "messages"
    ]
    expected_messages[1]["content"] = "Fix me please:\n\n%s" % (text)

    # Check prompt service
    ai_api_mock.chat_completion.assert_called_with(
        expected_messages,
        text,
        "improve-writing",
        {
            "model": "davinci",
            "temperature": 0.5,
            "top_p": 0.8,
            "max_tokens": 160,
        },
    )

    # Check slack message
    slack_service_mock.send_function_log_message.assert_called_with(
        "Improve Writing", text, "Jon's text"
    )

    check_log_message(
        "INFO", "[Authoring] Executing Improve Writing prompt..."
    )
    check_log_message("INFO", "[Authoring] Executed Improve Writing prompt")


# ----------------------------------------------
# ReduceReadingComplexityService
# ----------------------------------------------
def test_reduce_reading_complexity(
    make_prompt_templates_plain, check_log_message
):
    ai_api_mock = Mock()
    ai_api_mock.chat_completion.return_value = "Simpler text"
    assets_repo_mock = Mock()
    assets_repo_mock.get_json_asset.return_value = (
        make_prompt_templates_plain()
    )
    assets_filename = "assets_filename.json"
    slack_service_mock = Mock()

    # Build prompt service
    text = "Complex text"
    service = ReduceReadingComplexityService(
        ai_api_mock, assets_repo_mock, assets_filename, slack_service_mock
    )
    service.handle(text)

    expected_messages = make_prompt_templates_plain()[
        "ReduceReadingComplexity"
    ]["messages"]
    expected_messages[1]["content"] = "Simplify this:\n\n%s" % (text)

    # Check prompt service
    ai_api_mock.chat_completion.assert_called_with(
        expected_messages,
        text,
        "reduce-reading-complexity",
        {
            "model": "davinci",
            "temperature": 0.5,
            "top_p": 0.8,
            "max_tokens": 160,
        },
    )

    # Check slack message
    slack_service_mock.send_function_log_message.assert_called_with(
        "Reduce Reading Complexity", text, "Simpler text"
    )

    check_log_message(
        "INFO", "[Authoring] Executing Reduce Reading Complexity prompt..."
    )
    check_log_message(
        "INFO", "[Authoring] Executed Reduce Reading Complexity prompt"
    )


# ----------------------------------------------
# ReduceReadingTimeService
# ----------------------------------------------
def test_reduce_reading_time(make_prompt_templates_plain, check_log_message):
    ai_api_mock = Mock()
    ai_api_mock.chat_completion.return_value = "Simpler text"
    assets_repo_mock = Mock()
    assets_repo_mock.get_json_asset.return_value = (
        make_prompt_templates_plain()
    )
    assets_filename = "assets_filename.json"
    slack_service_mock = Mock()

    # Build prompt service
    text = "Complex text"
    service = ReduceReadingTimeService(
        ai_api_mock, assets_repo_mock, assets_filename, slack_service_mock
    )
    service.handle(text)

    expected_messages = make_prompt_templates_plain()["ReduceReadingTime"][
        "messages"
    ]
    expected_messages[1]["content"] = "Reduce time this:\n\n%s" % (text)

    # Check prompt service
    ai_api_mock.chat_completion.assert_called_with(
        expected_messages,
        text,
        "reduce-reading-time",
        {
            "model": "davinci",
            "temperature": 0.5,
            "top_p": 0.8,
            "max_tokens": 160,
        },
    )

    # Check slack message
    slack_service_mock.send_function_log_message.assert_called_with(
        "Reduce Reading Time", text, "Simpler text"
    )

    check_log_message(
        "INFO", "[Authoring] Executing Reduce Reading Time prompt..."
    )
    check_log_message(
        "INFO", "[Authoring] Executed Reduce Reading Time prompt"
    )


# ----------------------------------------------
# ExpandWritingService
# ----------------------------------------------
def test_expand_writing(make_prompt_templates_plain, check_log_message):
    ai_api_mock = Mock()
    ai_api_mock.chat_completion.return_value = "Expanded text"
    assets_repo_mock = Mock()
    assets_repo_mock.get_json_asset.return_value = (
        make_prompt_templates_plain()
    )
    assets_filename = "assets_filename.json"
    slack_service_mock = Mock()

    # Build prompt service
    text = "Complex text"
    service = ExpandWritingService(
        ai_api_mock, assets_repo_mock, assets_filename, slack_service_mock
    )
    service.handle(text)

    expected_messages = make_prompt_templates_plain()["ExpandWriting"][
        "messages"
    ]
    expected_messages[1]["content"] = "Expand writing of this:\n\n%s" % (text)

    # Check prompt service
    ai_api_mock.chat_completion.assert_called_with(
        expected_messages,
        text,
        "expand-writing",
        {
            "model": "davinci",
            "temperature": 0.5,
            "top_p": 0.8,
            "max_tokens": 160,
        },
    )

    # Check slack message
    slack_service_mock.send_function_log_message.assert_called_with(
        "Expand Writing", text, "Expanded text"
    )

    check_log_message("INFO", "[Authoring] Executing Expand Writing prompt...")
    check_log_message("INFO", "[Authoring] Executed Expand Writing prompt")
