from unittest.mock import patch

from src.builders.prompts import (
    ChangeTonePromptBuilder,
    ExpandWritingBuilder,
    FixGrammarPromptBuilder,
    ImproveWritingPromptBuilder,
    PromptBuilder,
    ReduceReadingComplexityBuilder,
    ReduceReadingTimeBuilder,
    SemanticSearchSummarizePrompt,
    SummarizeIntoStepsPromptBuilder,
    SummarizePromptBuilder,
    TranslatePromptBuilder,
)


# ----------------------------------------------
# PromptBuilder
# ----------------------------------------------
@patch("src.builders.prompts.PromptBuilder.__abstractmethods__", set())
def test_properties_default_values():
    builder = PromptBuilder()

    assert builder.template is None


@patch("src.builders.prompts.PromptBuilder.__abstractmethods__", set())
def test_properties_getters_and_setters():
    builder = PromptBuilder()
    builder.template = "Hello"

    assert builder.template == "Hello"


# ----------------------------------------------
# FixGrammarPromptBuilder
# ----------------------------------------------
def test_build_fix_grammar_prompt():
    builder = FixGrammarPromptBuilder("Testing template: {{text}}")

    assert builder.build("Hi!") == "Testing template: Hi!"


# ----------------------------------------------
# SummarizePromptBuilder
# ----------------------------------------------
def test_build_summarize_prompt(
    make_chat_completion_prompt, make_chat_completion_prompt_plain
):
    prompt = make_chat_completion_prompt()
    builder = SummarizePromptBuilder(prompt)

    expected_messages = make_chat_completion_prompt_plain()["messages"]
    expected_messages[-1]["content"] = "Shorten the text:\n\nHi!"

    assert builder.build("Hi!") == expected_messages


# ----------------------------------------------
# SummarizeIntoStepsPromptBuilder
# ----------------------------------------------
def test_build_summarize_into_steps_prompt(
    make_chat_completion_prompt, make_chat_completion_prompt_plain
):
    prompt = make_chat_completion_prompt()
    builder = SummarizeIntoStepsPromptBuilder(prompt)

    expected_messages = make_chat_completion_prompt_plain()["messages"]
    expected_messages[-1]["content"] = "Shorten the text:\n\nHi!"

    assert builder.build("Hi!") == expected_messages


# ----------------------------------------------
# ChangeTonePromptBuilder
# ----------------------------------------------
def test_build_change_tone_prompt(
    make_prompt_templates, make_prompt_templates_plain
):
    prompt = make_prompt_templates().ChangeTone
    builder = ChangeTonePromptBuilder(prompt)

    expected_messages = make_prompt_templates_plain()["ChangeTone"]["messages"]
    expected_messages[-1]["content"] = "Change to casual:\n\nHi!"

    assert builder.build("Hi!", "casual") == expected_messages


# ----------------------------------------------
# TranslatePromptBuilder
# ----------------------------------------------
def test_build_translate_prompt(
    make_prompt_templates, make_prompt_templates_plain
):
    prompt = make_prompt_templates().Translate
    builder = TranslatePromptBuilder(prompt)

    expected_messages = make_prompt_templates_plain()["Translate"]["messages"]
    expected_messages[-1]["content"] = "Translate to spanish:\n\nHi!"

    assert builder.build("Hi!", "spanish") == expected_messages


# ----------------------------------------------
# ImproveWritingPromptBuilder
# ----------------------------------------------
def test_build_improve_writing_prompt(
    make_prompt_templates, make_prompt_templates_plain
):
    prompt = make_prompt_templates().ImproveWriting
    builder = ImproveWritingPromptBuilder(prompt)

    expected_messages = make_prompt_templates_plain()["ImproveWriting"][
        "messages"
    ]
    expected_messages[-1]["content"] = "Fix me please:\n\nHi!"

    assert builder.build("Hi!") == expected_messages


# ----------------------------------------------
# ReduceReadingComplexityBuilder
# ----------------------------------------------
def test_build_reduce_reading_complexity_prompt(
    make_prompt_templates, make_prompt_templates_plain
):
    prompt = make_prompt_templates().ReduceReadingComplexity
    builder = ReduceReadingComplexityBuilder(prompt)

    expected_messages = make_prompt_templates_plain()[
        "ReduceReadingComplexity"
    ]["messages"]
    expected_messages[-1]["content"] = "Simplify this:\n\nHi!"

    assert builder.build("Hi!") == expected_messages


# ----------------------------------------------
# ReduceReadingTimeBuilder
# ----------------------------------------------
def test_build_reduce_reading_time_prompt(
    make_prompt_templates, make_prompt_templates_plain
):
    prompt = make_prompt_templates().ReduceReadingTime
    builder = ReduceReadingTimeBuilder(prompt)

    expected_messages = make_prompt_templates_plain()["ReduceReadingTime"][
        "messages"
    ]
    expected_messages[-1]["content"] = "Reduce time this:\n\nHi!"

    assert builder.build("Hi!") == expected_messages


# ----------------------------------------------
# ExpandWritingBuilder
# ----------------------------------------------
def test_build_expand_writing_prompt(
    make_prompt_templates, make_prompt_templates_plain
):
    prompt = make_prompt_templates().ExpandWriting
    builder = ExpandWritingBuilder(prompt)

    expected_messages = make_prompt_templates_plain()["ExpandWriting"][
        "messages"
    ]
    expected_messages[-1]["content"] = "Expand writing of this:\n\nHi!"

    assert builder.build("Hi!") == expected_messages


# ----------------------------------------------
# SummarizerPrompt
# ----------------------------------------------
def test_build_summarizer_prompt(make_summarizer_config_plain):
    config = make_summarizer_config_plain()

    builder = SemanticSearchSummarizePrompt(config["templates"]["short"])
    expected_prompt = "This is a short template with Context and Question"
    assert builder.build("Context", "Question") == expected_prompt

    builder = SemanticSearchSummarizePrompt(config["templates"]["long"])
    expected_prompt = "This is a very long template with Context and Question"
    assert builder.build("Context", "Question") == expected_prompt
