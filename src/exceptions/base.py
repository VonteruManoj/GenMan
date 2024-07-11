from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse

from src.schemas.endpoints.responses import BaseResponse


def base_exception_handler(
    request: Request, exc: BaseException
) -> JSONResponse:
    content = BaseResponse(
        error=True, error_code=exc.error_code, message=exc.message
    )

    return JSONResponse(status_code=exc.code, content=content.dict())


class BaseException(Exception):
    _code = HTTPStatus.BAD_GATEWAY
    _error_code = HTTPStatus.BAD_GATEWAY
    _message = HTTPStatus.BAD_GATEWAY.description

    def __init__(
        self,
        code: int = None,
        error_code: int = None,
        message: str = None,
    ) -> None:
        self._code = code if code is not None else self._code
        self._error_code = (
            error_code if error_code is not None else self._error_code
        )
        self._message = message if message is not None else self._message

    @property
    def code(self) -> int:
        return self._code

    @code.setter
    def code(self, code: int) -> None:
        self._code = code

    @property
    def error_code(self) -> int:
        return self._error_code

    @error_code.setter
    def error_code(self, error_code: int) -> None:
        self._error_code = error_code

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        self._message = message
