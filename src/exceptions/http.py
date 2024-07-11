from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.exceptions.base import BaseException
from src.schemas.endpoints.responses import HTTPValidationResponse


def custom_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    msg = (
        f"'{exc.errors()[0]['loc'][1]}': {exc.errors()[0]['msg']}"
        if len(exc.errors()) > 0
        else "Validation error"
    )
    content = HTTPValidationResponse(
        message=msg,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(content.dict()),
    )


class NotFoundException(BaseException):
    _code = 404
    _error_code = 4040
    _message = "Not found."


class ValidationException(BaseException):
    _code = 422
    _error_code = 4220
    _message = "Validation failed."
