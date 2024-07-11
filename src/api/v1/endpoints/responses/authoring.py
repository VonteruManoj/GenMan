from typing import List

from pydantic import BaseModel, Field

from src.schemas.endpoints.responses import BaseResponse, PaginationResponse


#################################################
# Metadata/Information
#################################################
class MetadataItem(BaseModel):
    max_tokens: int = Field(
        16,
        ge=1,
        le=4096,
        description="The maximum number of tokens to generate.",
    )

    disabled: bool = Field(
        False,
        description="The disabled status of the prompt.",
    )

    class Config:
        schema_extra = {"example": {"max_tokens": 256, "disabled": False}}


class MetadataData(BaseModel):
    FixGrammar: MetadataItem = Field(
        default=..., description="The metadata for the FixGrammar prompt."
    )
    Summarize: MetadataItem = Field(
        default=..., description="The metadata for the Summarize prompt."
    )
    SummarizeIntoSteps: MetadataItem = Field(
        default=...,
        description="The metadata for the SummarizeIntoSteps prompt.",
    )
    ChangeTone: MetadataItem = Field(
        default=..., description="The metadata for the ChangeTone prompt."
    )
    Translate: MetadataItem = Field(
        default=..., description="The metadata for the Translate prompt."
    )
    ImproveWriting: MetadataItem = Field(
        default=..., description="The metadata for the ImproveWriting prompt."
    )
    ReduceReadingComplexity: MetadataItem = Field(
        default=...,
        description="The metadata for the ReduceReadingComplexity prompt.",
    )
    ReduceReadingTime: MetadataItem = Field(
        default=...,
        description="The metadata for the ReduceReadingTime prompt.",
    )
    ExpandWriting: MetadataItem = Field(
        default=...,
        description="The metadata for the ExpandWriting prompt.",
    )

    class Config:
        schema_extra = {
            "example": {
                "FixGrammar": {
                    "max_tokens": 256,
                },
                "Summarize": {
                    "max_tokens": 256,
                },
                "SummarizeIntoSteps": {
                    "max_tokens": 256,
                },
                "ChangeTone": {
                    "max_tokens": 256,
                },
                "Translate": {
                    "max_tokens": 256,
                },
                "ImproveWriting": {
                    "max_tokens": 256,
                },
                "ReduceReadingComplexity": {
                    "max_tokens": 256,
                },
                "ReduceReadingTime": {
                    "max_tokens": 256,
                },
                "ExpandWriting": {
                    "max_tokens": 256,
                },
            }
        }


class MetadataResponse(BaseResponse):
    data: MetadataData


CHAIN_EXAMPLES = [
    {
        "id": 7,
        "operation": "summarize",
        "prompt": '[{"role": "system", "content": "You help'
        " people summarize into one paragraph. In case the user"
        " input is already summarized or is one paragraph, the"
        " output is the same input text. If you find words surrounded"
        ' by \\"#\\", they should be outputted the same way and should'
        ' always be in the output."}, {"role": "user", "content":'
        ' "Summarize in one paragraph:\\nText:\\n\\"\\"\\"\\nHi,'
        " welcome! You\\u2019re connected to Zingtree at Customer"
        ' Service. How may I help you?\\n\\"\\"\\""}]',
        "input": '"Hi, welcome! You\\u2019re connected to Zingtree'
        ' at Customer Service. How may I help you?"',
        "response": '{"id": "chatcmpl-7LwiVZlxmwPo4xiMnAP9nc5oRTb2e",'
        ' "object": "chat.completion", "created": 1685464951,'
        ' "model": "gpt-3.5-turbo-0301", "usage": {"prompt_tokens":'
        ' 98, "completion_tokens": 25, "total_tokens": 123},'
        ' "choices": [{"message": {"role": "assistant",'
        ' "content": "The user is connected to Zingtree\'s'
        " Customer Service and is being greeted. The representative"
        ' is asking how they can assist."}, "finish_reason":'
        ' "stop", "index": 0}]}',
        "output": "\"The user is connected to Zingtree's Customer"
        " Service and is being greeted. The representative is"
        ' asking how they can assist."',
        "created_at": "2023-05-30 16:42:35.000000",
    },
    {
        "id": 8,
        "operation": "moderation",
        "prompt": "\"The user is connected to Zingtree's Customer"
        " Service and is being greeted. The representative"
        ' is asking how they can assist."',
        "input": "\"The user is connected to Zingtree's Customer"
        " Service and is being greeted."
        ' The representative is asking how they can assist."',
        "response": '{"id": "modr-7LwiZLiu4Vi5VN4RagxoGhXwvuVUf",'
        ' "model": "text-moderation-004", "results": [{"flagged":'
        ' false, "categories": {"sexual": false, "hate": false,'
        ' "violence": false, "self-harm": false, "sexual/minors":'
        ' false, "hate/threatening": false, "violence/graphic":'
        ' false}, "category_scores": {"sexual": 7.41601e-06,'
        ' "hate": 1.5529113e-06, "violence": 3.5277565e-06,'
        ' "self-harm": 9.301131e-09, "sexual/minors":'
        ' 5.8955743e-07, "hate/threatening": 8.217987e-11,'
        ' "violence/graphic": 4.0216787e-06}}]}',
        "output": "false",
        "created_at": "2023-05-30 16:42:36.000000",
    },
]


class ChainLink(BaseModel):
    id: int = Field(default=..., description="The id of the chain link.")
    operation: str = Field(
        default=..., description="The function name of the chain link."
    )
    prompt: str = Field(
        default=..., description="The prompt of the chain link."
    )
    input: str = Field(default=..., description="The input of the chain link.")
    response: str = Field(
        default=..., description="The response of the chain link."
    )
    output: str = Field(
        default=..., description="The output of the chain link."
    )
    created_at: str = Field(
        default=..., description="The created at of the chain link."
    )

    class Config:
        schema_extra = {"example": CHAIN_EXAMPLES[0]}


class UsageItem(BaseModel):
    chain_id: str = Field(
        default=..., description="The group id of the prompt."
    )
    chain_operation: str = Field(
        default=..., description="The group function of the prompt."
    )
    user_id: int = Field(default=..., description="The user id of the prompt.")
    org_id: int = Field(
        default=..., description="The organization id of the prompt."
    )
    project_id: int = Field(
        default=..., description="The project id of the prompt."
    )
    chain_links: List[ChainLink] = Field(
        default=..., description="The chain links of the prompt."
    )

    class Config:
        schema_extra = {
            "example": {
                "chain_id": 1,
                "chain_operation": "fix-grammar",
                "user_id": 1,
                "org_id": 1,
                "project_id": 1,
                "chain_links": CHAIN_EXAMPLES,
            }
        }


class UsageResponse(PaginationResponse):
    data: List[UsageItem]


#################################################
# Prompts
#################################################
class FixGrammarData(BaseModel):
    text: str = Field(
        default=..., description="The grammatically correct text."
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "Turn every human into an expert.",
            }
        }


class FixGrammarResponse(BaseResponse):
    data: FixGrammarData


class SummarizeData(BaseModel):
    text: str = Field(default=..., description="The summarized text.")

    class Config:
        schema_extra = {
            "example": {
                "text": "Hi, welcome! How may I help you?",
            }
        }


class SummarizeResponse(BaseResponse):
    data: SummarizeData


class SummarizeIntoStepsData(BaseModel):
    text: str = Field(
        default=..., description="The summarized into steps text."
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "1. The text begins with a greeting.\n\n2."
                " It introduces the speaker and provides an"
                " opportunity for the reader to state their need."
                "\n\n3. The speaker offers assistance.",
            }
        }


class SummarizeIntoStepsResponse(BaseResponse):
    data: SummarizeIntoStepsData


class ChangeToneData(BaseModel):
    text: str = Field(
        default=..., description="The rewritten text with the given tone."
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "Hey there! Welcome to Customer Service."
                " I'm Carlos. What can I do for you?",
            }
        }


class ChangeToneResponse(BaseResponse):
    data: ChangeToneData


class TranslateData(BaseModel):
    text: str = Field(default=..., description="The translated text.")

    class Config:
        schema_extra = {
            "example": {"text": "Buongiorno! Benvenuto al Servizio Clienti."}
        }


class TranslateResponse(BaseResponse):
    data: TranslateData


class ImproveWritingData(BaseModel):
    text: str = Field(
        default=..., description="The rewritten text with the improvements."
    )

    class Config:
        schema_extra = {"example": {"text": "This is Jon's text."}}


class ImproveWritingResponse(BaseResponse):
    data: ImproveWritingData


class ReduceReadingComplexityData(BaseModel):
    text: str = Field(
        default=..., description="The rewritten text with the improvements."
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "In today's fast-changing world of"
                " technology, it's crucial for people to have"
                " a wide range of digital skills to handle"
                " the complexities of modern life. With the"
                " constant growth of global information"
                " networks, it's important to stay curious"
                " and adaptable in order to succeed in an"
                " era defined by constant innovation and"
                " change. Recognizing the connection between"
                " human intelligence and technology opens up"
                " exciting opportunities to explore new"
                " ideas and go beyond traditional limits.",
            }
        }


class ReduceReadingComplexityResponse(BaseResponse):
    data: ReduceReadingComplexityData


class ReduceReadingTimeData(BaseModel):
    text: str = Field(
        default=..., description="The rewritten text with the improvements."
    )

    class Config:
        schema_extra = {
            "example": {
                "In our fast-paced digital world, having diverse technological"
                " skills is crucial. With the constant growth of global"
                " information networks, being curious and adaptable is vital"
                " for success in an era of continuous innovation. Embracing"
                " the connection between human intellect and technology"
                " unlocks exciting possibilities beyond traditional"
                " boundaries."
            }
        }


class ReduceReadingTimeResponse(BaseResponse):
    data: ReduceReadingTimeData


class ExpandWritingData(BaseModel):
    text: str = Field(
        default=...,
        description="The text to be rewritten with a expanded writing.",
    )

    class Config:
        schema_extra = {
            "example": {
                "Good morning, and thank you for choosing our Customer"
                " Service. Here at our service center, we always"
                " strive to provide the best possible assistance"
                " to our valued customers. My name is Carlos, and"
                " I am pleased to assist you today. Please let me"
                " know how I may be of service to you, and I will"
                " do everything in my power to ensure your"
                " satisfaction."
            }
        }


class ExpandWritingResponse(BaseResponse):
    data: ExpandWritingData
