from typing import Optional

from pydantic import BaseModel, Field


class BasePrompt(BaseModel):
    platform: str = "OpenAI"
    model: str
    temperature: Optional[float] = Field(1.0, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(16, ge=1, le=4096)

    # This is available for all prompts
    # but is not used by this service
    # so we exclude it from the configs
    # disabled: bool = False

    def get_configs(self) -> dict:
        return self.dict(exclude={"platform"})


class CompletionPrompt(BasePrompt):
    prompt: str

    def get_configs(self) -> dict:
        return self.dict(exclude={"platform", "prompt"})


class ComposeChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionPrompt(BasePrompt):
    messages: list[ComposeChatMessage]

    def get_configs(self) -> dict:
        return self.dict(exclude={"platform", "messages"})


class PromptTemplates(BaseModel):
    FixGrammar: CompletionPrompt
    Summarize: ChatCompletionPrompt
    SummarizeIntoSteps: ChatCompletionPrompt
    ChangeTone: ChatCompletionPrompt
    Translate: ChatCompletionPrompt
    ImproveWriting: ChatCompletionPrompt
    ReduceReadingComplexity: ChatCompletionPrompt
    ReduceReadingTime: ChatCompletionPrompt
    ExpandWriting: ChatCompletionPrompt
