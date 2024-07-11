import pytest
from pydantic import ValidationError

from src.api.v1.endpoints.requests.authoring import (
    ChangeToneRequest,
    ExpandWritingRequest,
    FixGrammarRequest,
    ImproveWritingRequest,
    ReduceReadingComplexityRequest,
    ReduceReadingTimeRequest,
    SummarizeIntoStepsRequest,
    SummarizeRequest,
    TranslateRequest,
)


def test_fix_grammar_request():
    assert FixGrammarRequest(
        text="Turn every huan into an expert.",
        metadata={"user_id": 1, "org_id": 2, "project_id": 3},
    )


def test_fix_grammar_request_missing_fields():
    with pytest.raises(ValidationError):
        FixGrammarRequest()


def test_summarize_request_required_fields():
    assert SummarizeRequest(
        text="Turn every human into an expert.",
        metadata={"user_id": 1, "org_id": 2, "project_id": 3},
    )


def test_summarize_request_missing_fields():
    with pytest.raises(ValidationError):
        SummarizeRequest()


def test_summarize_into_steps_request_required_fields():
    assert SummarizeIntoStepsRequest(
        text="Good morning! Welcome to Customer Service."
        " My name is Carlos. How can I help you?",
        metadata={"user_id": 1, "org_id": 2, "project_id": 3},
    )


def test_summarize_into_steps_request_missing_fields():
    with pytest.raises(ValidationError):
        SummarizeIntoStepsRequest()


def test_change_tone_request_required_fields():
    assert ChangeToneRequest(
        text="Good morning! Welcome to Customer Service."
        " My name is Carlos. How can I help you?",
        tone="friendly",
        metadata={"user_id": 1, "org_id": 2, "project_id": 3},
    )


def test_change_tone_request_missing_fields():
    with pytest.raises(ValidationError):
        ChangeToneRequest()


def test_translate_request_required_fields():
    assert TranslateRequest(
        text="Hello! Welcome to Customer Service.",
        language="italian",
        metadata={"user_id": 1, "org_id": 2, "project_id": 3},
    )


def test_translate_request_missing_fields():
    with pytest.raises(ValidationError):
        TranslateRequest()

    with pytest.raises(ValidationError):
        TranslateRequest(language="italian")

    with pytest.raises(ValidationError):
        TranslateRequest(text="Hello! Welcome to Customer Service.")


def test_improve_writing_request_required_fields():
    assert ImproveWritingRequest(
        text="Good morning! Welcome to Customer Service."
        " My name is Carlos. How can I help you?",
        metadata={"user_id": 1, "org_id": 2, "project_id": 3},
    )


def test_improve_writing_request_missing_fields():
    with pytest.raises(ValidationError):
        ImproveWritingRequest()


def test_reduce_reading_complexity_request_required_field():
    assert ReduceReadingComplexityRequest(
        text="Random text",
        metadata={"user_id": 1, "org_id": 2, "project_id": 3},
    )


def test_reduce_reading_complexity_request_missing_fields():
    with pytest.raises(ValidationError):
        ReduceReadingComplexityRequest()


def test_reduce_reading_time_request_required_field():
    assert ReduceReadingTimeRequest(
        text="Random text",
        metadata={"user_id": 1, "org_id": 2, "project_id": 3},
    )


def test_reduce_reading_time_request_missing_fields():
    with pytest.raises(ValidationError):
        ReduceReadingTimeRequest()


def test_expand_writing_request_required_field():
    assert ExpandWritingRequest(
        text="Random text",
        metadata={"user_id": 1, "org_id": 2, "project_id": 3},
    )


def test_expand_writing_request_missing_fields():
    with pytest.raises(ValidationError):
        ExpandWritingRequest()
