from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class BaseResponse(BaseModel):
    error: bool = False
    error_code: Optional[int]
    message: Optional[str]
    # data: any


class BooleanResponse(BaseResponse):
    data: bool


class HTTPValidationResponse(BaseResponse):
    error: bool = True
    error_code: int = 4220
    message: str = "Validation error"

    class Config:
        schema_extra = {
            "error": True,
            "error_code": 4220,
            "message": "'limit': should be greater than 0.",
        }


class PaginationResponseMeta(GenericModel):
    current_page: int
    from_: int
    last_page: int
    per_page: int
    to: int
    total: int

    class Config:
        fields = {"from_": "from"}


class PaginationResponse(BaseResponse, Generic[T]):
    meta: PaginationResponseMeta
    data: List[T]
