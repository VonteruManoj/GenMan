import pytest

from src.schemas.assets.prompts import (
    BasePrompt,
    ChatCompletionPrompt,
    CompletionPrompt,
    ComposeChatMessage,
)


# ----------------------------------------------
# BasePrompt
# ----------------------------------------------
def test_base_prompt_get_json_configs(make_base_prompt):
    prompt_config = make_base_prompt()

    assert prompt_config.get_configs() == {
        "model": "davinci",
        "temperature": 0.5,
        "top_p": 0.8,
        "max_tokens": 160,
    }


def test_base_prompt_default_values(make_base_prompt_plain):
    obj = make_base_prompt_plain()
    del obj["platform"]
    del obj["temperature"]
    del obj["top_p"]
    del obj["max_tokens"]
    prompt_config = BasePrompt.parse_obj(obj)

    assert prompt_config.platform == "OpenAI"
    assert prompt_config.temperature == 1.0
    assert prompt_config.top_p == 1.0
    assert prompt_config.max_tokens == 16


invalid_values_for_base_prompt = [
    {"temperature": 2.1},
    {"top_p": 1.1},
    {"max_tokens": 4097},
    {"temperature": -0.1},
    {"top_p": -0.1},
    {"max_tokens": 0},
]


@pytest.mark.parametrize("override", invalid_values_for_base_prompt)
def test_base_prompt_validation_values(override, make_base_prompt_plain):
    obj = make_base_prompt_plain(**override)

    with pytest.raises(ValueError):
        BasePrompt.parse_obj(obj)


def test_base_prompt_minimun_fields():
    obj = {"model": "davinci"}

    assert isinstance(BasePrompt.parse_obj(obj), BasePrompt)


# ----------------------------------------------
# CompletionPrompt
# ----------------------------------------------
def test_completion_prompt_get_json_configs(make_completion_prompt):
    prompt_config = make_completion_prompt()

    assert prompt_config.get_configs() == {
        "model": "davinci",
        "temperature": 0.5,
        "top_p": 0.8,
        "max_tokens": 160,
    }


def test_completion_prompt_minimun_fields():
    obj = {"model": "davinci", "prompt": "Fix spelling and grammatical errors"}

    assert isinstance(CompletionPrompt.parse_obj(obj), CompletionPrompt)


# ----------------------------------------------
# ComposeChatMessage
# ----------------------------------------------
def test_compose_chat_message_minimun_fields():
    obj = {"role": "davinci", "content": "Fix spelling and grammatical errors"}

    assert isinstance(ComposeChatMessage.parse_obj(obj), ComposeChatMessage)


# ----------------------------------------------
# ChatCompletionPrompt
# ----------------------------------------------
def test_chat_completion_prompt_get_json_configs(make_chat_completion_prompt):
    prompt_config = make_chat_completion_prompt()

    assert prompt_config.get_configs() == {
        "model": "davinci",
        "temperature": 0.5,
        "top_p": 0.8,
        "max_tokens": 160,
    }


def test_chat_completion_prompt_minimun_fields(
    make_chat_completion_prompt_plain,
):
    obj = {
        "model": "davinci",
        "messages": make_chat_completion_prompt_plain()["messages"],
    }
    chat_completion_prompt = ChatCompletionPrompt.parse_obj(obj)

    assert isinstance(chat_completion_prompt, ChatCompletionPrompt)

    for message in chat_completion_prompt.messages:
        assert isinstance(message, ComposeChatMessage)


# ----------------------------------------------
# PromptsTemplates
# ----------------------------------------------
def test_fix_grammar_prompt_is_completion(make_prompt_templates):
    prompts_config = make_prompt_templates()

    assert isinstance(prompts_config.FixGrammar, CompletionPrompt)


def test_summarize_prompt_is_chat_completion(make_prompt_templates):
    prompts_config = make_prompt_templates()

    assert isinstance(prompts_config.Summarize, ChatCompletionPrompt)


def test_summarize_into_steps_prompt_is_chat_completion(make_prompt_templates):
    prompts_config = make_prompt_templates()

    assert isinstance(prompts_config.SummarizeIntoSteps, ChatCompletionPrompt)


def test_change_tone_prompt_is_chat_completion(make_prompt_templates):
    prompts_config = make_prompt_templates()

    assert isinstance(prompts_config.ChangeTone, ChatCompletionPrompt)


def test_translate_prompt_is_chat_completion(make_prompt_templates):
    prompts_config = make_prompt_templates()

    assert isinstance(prompts_config.Translate, ChatCompletionPrompt)


def test_improve_writing_prompt_is_chat_completion(make_prompt_templates):
    prompts_config = make_prompt_templates()

    assert isinstance(prompts_config.ImproveWriting, ChatCompletionPrompt)


def test_reduce_reading_complexity_prompt_is_chat_completion(
    make_prompt_templates,
):
    prompts_config = make_prompt_templates()

    assert isinstance(
        prompts_config.ReduceReadingComplexity, ChatCompletionPrompt
    )


def test_reduce_reading_time_prompt_is_chat_completion(
    make_prompt_templates,
):
    prompts_config = make_prompt_templates()

    assert isinstance(prompts_config.ReduceReadingTime, ChatCompletionPrompt)


def test_expand_writing_prompt_is_chat_completion(
    make_prompt_templates,
):
    prompts_config = make_prompt_templates()

    assert isinstance(prompts_config.ExpandWriting, ChatCompletionPrompt)
