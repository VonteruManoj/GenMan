import pytest

from src.exceptions.http import NotFoundException


def test_contet_policy_violation_exception():
    with pytest.raises(NotFoundException) as e:
        raise NotFoundException()

    assert e.value.code == 404
    assert e.value.error_code == 4040
    assert e.value.message == "Not found."
