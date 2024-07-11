from src.exceptions.base import BaseException


class AIApiResponseFormatException(BaseException):
    _code = 500
    _error_code = 5000
    _message = "Api AI response format exception."
