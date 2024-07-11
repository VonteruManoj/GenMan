from enum import Enum


class AuthoringPromptsOperationNames(Enum):
    FIX_GRAMMAR = "fix-grammar"
    SUMMARIZE = "summarize"
    SUMMARIZE_INTO_STEPS = "summarize-into-steps"
    CHANGE_TONE = "change-tone"
    TRANSLATE = "translate"
    IMPROVE_WRITING = "improve-writing"
    REDUCE_READING_COMPLEXITY = "reduce-reading-complexity"
    REDUCE_READING_TIME = "reduce-reading-time"
    EXPAND_WRITING = "expand-writing"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
