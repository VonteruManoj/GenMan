from src.schemas.endpoints.responses import BaseResponse


# ----------------------------------------------
# BaseResponse
# ----------------------------------------------
def test_base_response():
    response = BaseResponse()

    assert response == {
        "error": False,
        "error_code": None,
        "message": None,
    }
