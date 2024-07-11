from enum import Enum


class ModerationPromptsOperationNames(Enum):
    MODERATION = "moderation"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
