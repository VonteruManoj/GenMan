from fastapi.responses import JSONResponse

from src.exceptions.base import BaseException, base_exception_handler


def test_base_exception_handler_response():
    request = None
    exc = BaseException(message="Bad Gateway")
    response = base_exception_handler(request, exc)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 502

    assert (
        response.body == b'{"error":true,"error_code":502,"message":'
        b'"Bad Gateway"}'
    )


# ----------------------------------------------
# BaseException
# ----------------------------------------------
def test_base_exception_default_values():
    exc = BaseException()

    assert exc.code == 502
    assert exc.error_code == 502
    assert exc.message == "Invalid responses from another server/proxy"


def test_base_exception_getters_and_setters():
    exc = BaseException()
    exc.code = 400
    exc.error_code = 400
    exc.message = "Bad Request"

    assert exc.code == 400
    assert exc.error_code == 400
    assert exc.message == "Bad Request"
