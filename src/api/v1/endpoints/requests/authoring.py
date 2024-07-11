from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, Field


class AuditMetadata(BaseModel):
    user_id: int
    org_id: int
    project_id: int


class FixGrammarRequest(BaseModel):
    metadata: AuditMetadata
    text: str = Field(
        default=..., description="The text to be grammatically corrected."
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "Turn every huan into an expert.",
                "metadata": {
                    "user_id": 1,
                    "org_id": 1,
                    "project_id": 1,
                },
            }
        }


class SummarizeRequest(BaseModel):
    metadata: AuditMetadata
    text: str = Field(default=..., description="The text to be summarized.")

    class Config:
        schema_extra = {
            "example": {
                "text": "Hi, welcome! You’re connected to Zingtree"
                " at Customer Service. How may I help you?",
                "metadata": {
                    "user_id": 1,
                    "org_id": 1,
                    "project_id": 1,
                },
            }
        }


class SummarizeIntoStepsRequest(BaseModel):
    metadata: AuditMetadata
    text: str = Field(
        default=..., description="The text to be summarized into steps."
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "Good morning! Welcome to Customer Service."
                " My name is Carlos. How can I help you?",
                "metadata": {
                    "user_id": 1,
                    "org_id": 1,
                    "project_id": 1,
                },
            }
        }


class ChangeToneRequest(BaseModel):
    metadata: AuditMetadata
    tone: str = Field(
        default=..., description="The tone used to rewritten the given text."
    )
    text: str = Field(
        default=...,
        description="The text to be rewritten with a specific tone.",
    )

    class Config:
        schema_extra = {
            "example": {
                "tone": "casual",
                "text": "Good morning! Welcome to Customer Service."
                " My name is Carlos. How can I help you?",
                "metadata": {
                    "user_id": 1,
                    "org_id": 1,
                    "project_id": 1,
                },
            }
        }


class TranslateRequest(BaseModel):
    metadata: AuditMetadata
    language: str = Field(default=..., description="The language to be used.")
    text: str = Field(
        default=...,
        description="The text to be translated.",
    )

    class Config:
        schema_extra = {
            "example": {
                "language": "italian",
                "text": "Good morning! Welcome to Customer Service.",
                "metadata": {
                    "user_id": 1,
                    "org_id": 1,
                    "project_id": 1,
                },
            }
        }


class ImproveWritingRequest(BaseModel):
    metadata: AuditMetadata
    text: str = Field(
        default=...,
        description="The text to be rewritten with improvements.",
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "This is the text of Jon.",
                "metadata": {
                    "user_id": 1,
                    "org_id": 1,
                    "project_id": 1,
                },
            }
        }


class ReduceReadingComplexityRequest(BaseModel):
    metadata: AuditMetadata
    text: str = Field(
        default=...,
        description="The text to be rewritten"
        " with reduced reading complexity.",
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "Immersed within the intricacies of a rapidly"
                " evolving technological landscape, it becomes"
                " increasingly paramount for individuals to harness"
                " a multifaceted repertoire of digital competencies"
                " to navigate the complexities of modern existence."
                " As the interconnected web of global information"
                " continues to expand exponentially, one must cultivate"
                " an insatiable curiosity and an adaptive mindset to"
                " thrive in an era characterized by perpetual"
                " innovation and relentless disruption. Embracing the"
                " symbiotic relationship between human intellect and"
                " technological advancements unveils unprecedented"
                " possibilities, urging us to transcend conventional"
                " boundaries and embark upon an intellectual odyssey"
                " that transcends the constraints of tradition.",
                "metadata": {
                    "user_id": 1,
                    "org_id": 1,
                    "project_id": 1,
                },
            }
        }


class ReduceReadingTimeRequest(BaseModel):
    metadata: AuditMetadata
    text: str = Field(
        default=...,
        description="The text to be rewritten with reduced reading time.",
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "Immersed within the intricacies of a rapidly"
                " evolving technological landscape, it becomes"
                " increasingly paramount for individuals to harness"
                " a multifaceted repertoire of digital competencies"
                " to navigate the complexities of modern existence."
                " As the interconnected web of global information"
                " continues to expand exponentially, one must cultivate"
                " an insatiable curiosity and an adaptive mindset to"
                " thrive in an era characterized by perpetual"
                " innovation and relentless disruption. Embracing the"
                " symbiotic relationship between human intellect and"
                " technological advancements unveils unprecedented"
                " possibilities, urging us to transcend conventional"
                " boundaries and embark upon an intellectual odyssey"
                " that transcends the constraints of tradition.",
                "metadata": {
                    "user_id": 1,
                    "org_id": 1,
                    "project_id": 1,
                },
            }
        }


class ExpandWritingRequest(BaseModel):
    metadata: AuditMetadata
    text: str = Field(
        default=...,
        description="The text to be rewritten with a expanded writing.",
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "Good morning! Welcome to Customer Service. My"
                " name is Carlos. How can I help you?",
                "metadata": {
                    "user_id": 1,
                    "org_id": 1,
                    "project_id": 1,
                },
            }
        }


class UsageQueryRequest:
    def __init__(
        self,
        page: Optional[int] = Query(1, ge=1),
        per_page: Optional[int] = Query(10, ge=1, le=100),
        sort_by: Optional[str] = Query("created_at"),
        sort_dir: Optional[str] = Query("desc"),
        search: Optional[str] = Query(None),
        start_date: Optional[str] = Query(None),
        end_date: Optional[str] = Query(None),
        org_id: Optional[int] = Query(None),
        prompts: Optional[List[str]] = Query(None),
        failed: Optional[bool] = Query(None),
    ):
        self.page = page
        self.per_page = per_page
        self.sort_by = sort_by
        self.sort_dir = sort_dir
        self.search = search
        self.start_date = start_date
        self.end_date = end_date
        self.org_id = org_id
        self.prompts = prompts
        self.failed = failed
