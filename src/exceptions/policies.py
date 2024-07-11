from src.exceptions.base import BaseException


class ContentPolicyViolationException(BaseException):
    _code = 200
    _error_code = 4019
    _message = "The given text is flagged as violating content policy."
