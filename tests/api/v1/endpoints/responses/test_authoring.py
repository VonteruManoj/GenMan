import pytest
from pydantic import ValidationError

from src.api.v1.endpoints.responses.authoring import (
    ChangeToneData,
    ChangeToneResponse,
    ExpandWritingData,
    ExpandWritingResponse,
    FixGrammarData,
    FixGrammarResponse,
    ImproveWritingData,
    ImproveWritingResponse,
    MetadataData,
    MetadataResponse,
    ReduceReadingComplexityData,
    ReduceReadingComplexityResponse,
    ReduceReadingTimeData,
    ReduceReadingTimeResponse,
    SummarizeData,
    SummarizeIntoStepsData,
    SummarizeIntoStepsResponse,
    SummarizeResponse,
    TranslateData,
    TranslateResponse,
)


#################################################
# Metadata/Information
#################################################
def test_metadata_response(make_prompt_templates_plain):
    assert MetadataResponse(
        data=MetadataData.parse_obj(make_prompt_templates_plain())
    )


def test_metadata_response_has_disabled(make_prompt_templates_plain):
    data = make_prompt_templates_plain()
    data["FixGrammar"]["disabled"] = True
    meta = MetadataResponse(data=MetadataData.parse_obj(data))

    # Testing case
    assert meta.data.FixGrammar.disabled is True
    # Default case
    assert meta.data.Summarize.disabled is False


def test_metadata_response_missing_fields():
    with pytest.raises(ValidationError):
        MetadataResponse()


#################################################
# Prompts
#################################################
def test_fix_grammar_response():
    assert FixGrammarResponse(
        data=FixGrammarData(text="Turn every huan into an expert.")
    )


def test_fix_grammar_response_missing_fields():
    with pytest.raises(ValidationError):
        FixGrammarResponse()


def test_summarize_response_required_fields():
    assert SummarizeResponse(
        data=SummarizeData(text="Turn every human into an expert.")
    )


def test_summarize_response_missing_fields():
    with pytest.raises(ValidationError):
        SummarizeResponse()


def test_summarize_into_steps_response_required_fields():
    assert SummarizeIntoStepsResponse(
        data=SummarizeIntoStepsData(
            text="1. The text begins with a greeting.\n\n2."
            " It introduces the speaker and provides an"
            " opportunity for the reader to state their need."
            "\n\n3. The speaker offers assistance."
        )
    )


def test_summarize_into_steps_response_missing_fields():
    with pytest.raises(ValidationError):
        SummarizeIntoStepsResponse()


def test_change_tone_response_required_fields():
    assert ChangeToneResponse(
        data=ChangeToneData(text="Turn every human into an expert.")
    )


def test_change_tone_response_missing_fields():
    with pytest.raises(ValidationError):
        ChangeToneResponse()


def test_translate_response_required_fields():
    assert TranslateResponse(
        data=TranslateData(text="Buongiorno! Benvenuto al Servizio Clienti.")
    )


def test_translate_response_missing_fields():
    with pytest.raises(ValidationError):
        TranslateResponse()


def test_improve_writing_response_required_fields():
    assert ImproveWritingResponse(
        data=ImproveWritingData(text="Turn every human into an expert.")
    )


def test_improve_writing_response_missing_fields():
    with pytest.raises(ValidationError):
        ImproveWritingResponse()


def test_reduce_reading_complexity_response_required_fields():
    assert ReduceReadingComplexityResponse(
        data=ReduceReadingComplexityData(text="Simpler text.")
    )


def test_reduce_reading_complexity_response_missing_fields():
    with pytest.raises(ValidationError):
        ReduceReadingComplexityResponse()


def test_reduce_reading_time_response_required_fields():
    assert ReduceReadingTimeResponse(
        data=ReduceReadingTimeData(text="Simpler text.")
    )


def test_reduce_reading_time_response_missing_fields():
    with pytest.raises(ValidationError):
        ReduceReadingTimeResponse()


def test_expand_writing_response_required_fields():
    assert ExpandWritingResponse(data=ExpandWritingData(text="Expanded text."))


def test_expand_writing_response_missing_fields():
    with pytest.raises(ValidationError):
        ExpandWritingResponse()
