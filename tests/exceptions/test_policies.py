import pytest

from src.exceptions.policies import ContentPolicyViolationException


def test_contet_policy_violation_exception():
    with pytest.raises(ContentPolicyViolationException) as e:
        raise ContentPolicyViolationException()

    assert e.value.code == 200
    assert e.value.error_code == 4019
    assert (
        e.value.message
        == "The given text is flagged as violating content policy."
    )
