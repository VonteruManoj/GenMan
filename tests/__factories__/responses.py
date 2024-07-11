def make_successful_response_wrapper_plain():
    def make(**rest):
        return {
            "error": False,
            "error_code": None,
            "message": None,
            "data": {**rest},
        }

    return make
