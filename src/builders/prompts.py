from abc import ABC, abstractmethod

from src.schemas.assets.prompts import (
    BasePrompt,
    ChatCompletionPrompt,
    CompletionPrompt,
)


class PromptBuilder(ABC):
    def __init__(self, template: any = None) -> None:
        self._template = template

    @property
    def template(self) -> BasePrompt:
        return self._template

    @template.setter
    def template(self, template: BasePrompt) -> None:
        self._template = template

    @abstractmethod
    def build(self, text: str) -> any:
        raise NotImplementedError


class CompletionPromptBuilder(PromptBuilder):
    @property
    def template(self) -> CompletionPrompt:
        return self._template

    @template.setter
    def template(self, template: CompletionPrompt) -> None:
        self._template = template


class ChatCompletionPromptBuilder(CompletionPromptBuilder):
    @property
    def template(self) -> ChatCompletionPrompt:
        return self._template

    @template.setter
    def template(self, template: ChatCompletionPrompt) -> None:
        self._template = template


class FixGrammarPromptBuilder(CompletionPromptBuilder):
    def build(self, text: str) -> str:
        return self.template.replace("{{text}}", text)


class SummarizePromptBuilder(ChatCompletionPromptBuilder):
    def build(self, text: str) -> list[dict]:
        messages = [m.dict() for m in self.template.messages]
        messages[-1]["content"] = messages[-1]["content"].replace(
            "{{text}}", text
        )

        return messages


class SummarizeIntoStepsPromptBuilder(ChatCompletionPromptBuilder):
    def build(self, text: str) -> list[dict]:
        messages = [m.dict() for m in self.template.messages]
        messages[-1]["content"] = messages[-1]["content"].replace(
            "{{text}}", text
        )

        return messages


class ChangeTonePromptBuilder(ChatCompletionPromptBuilder):
    def build(self, text: str, tone: str) -> list[dict]:
        messages = [m.dict() for m in self.template.messages]
        messages[-1]["content"] = messages[-1]["content"].replace(
            "{{text}}", text
        )
        messages[-1]["content"] = messages[-1]["content"].replace(
            "{{tone}}", tone
        )

        return messages


class TranslatePromptBuilder(ChatCompletionPromptBuilder):
    def build(self, text: str, language: str) -> list[dict]:
        messages = [m.dict() for m in self.template.messages]
        messages[-1]["content"] = messages[-1]["content"].replace(
            "{{text}}", text
        )
        messages[-1]["content"] = messages[-1]["content"].replace(
            "{{language}}", language
        )

        return messages


class ImproveWritingPromptBuilder(ChatCompletionPromptBuilder):
    def build(self, text: str) -> list[dict]:
        messages = [m.dict() for m in self.template.messages]
        messages[-1]["content"] = messages[-1]["content"].replace(
            "{{text}}", text
        )

        return messages


class ReduceReadingComplexityBuilder(ChatCompletionPromptBuilder):
    def build(self, text: str) -> list[dict]:
        messages = [m.dict() for m in self.template.messages]
        messages[-1]["content"] = messages[-1]["content"].replace(
            "{{text}}", text
        )

        return messages


class ReduceReadingTimeBuilder(ChatCompletionPromptBuilder):
    def build(self, text: str) -> list[dict]:
        messages = [m.dict() for m in self.template.messages]
        messages[-1]["content"] = messages[-1]["content"].replace(
            "{{text}}", text
        )

        return messages


class ExpandWritingBuilder(ChatCompletionPromptBuilder):
    def build(self, text: str) -> list[dict]:
        messages = [m.dict() for m in self.template.messages]
        messages[-1]["content"] = messages[-1]["content"].replace(
            "{{text}}", text
        )

        return messages


class SemanticSearchSummarizePrompt(PromptBuilder):
    def build(self, context: str, question: str) -> str:
        return self.template.replace("{{context}}", context).replace(
            "{{question}}", question
        )
