import copy

import tests.__stubs__.prompt_templates as prompt_templates_stubs
from src.schemas.assets.prompts import (
    BasePrompt,
    ChatCompletionPrompt,
    CompletionPrompt,
    PromptTemplates,
)


def make_base_prompt_plain():
    def make(**rest):
        return copy.deepcopy(prompt_templates_stubs.BASE_PROMPT) | {**rest}

    return make


def make_completion_prompt_plain():
    def make(**rest):
        return copy.deepcopy(prompt_templates_stubs.COMPLETION_PROMPT) | {
            **rest
        }

    return make


def make_chat_completion_prompt_plain():
    def make(**rest):
        return copy.deepcopy(prompt_templates_stubs.CHAT_COMPLETION_PROMPT) | {
            **rest
        }

    return make


def make_prompt_templates_plain():
    def make(**rest):
        return copy.deepcopy(prompt_templates_stubs.PROMPT_TEMPLATES) | {
            **rest
        }

    return make


def make_base_prompt():
    def make(**rest):
        return BasePrompt.parse_obj(make_base_prompt_plain()(**rest))

    return make


def make_completion_prompt():
    def make(**rest):
        return CompletionPrompt.parse_obj(
            make_completion_prompt_plain()(**rest)
        )

    return make


def make_chat_completion_prompt():
    def make(**rest):
        return ChatCompletionPrompt.parse_obj(
            make_chat_completion_prompt_plain()(**rest)
        )

    return make


def make_prompt_templates():
    def make(**rest):
        return PromptTemplates.parse_obj(make_prompt_templates_plain()(**rest))

    return make
