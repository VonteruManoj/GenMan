from unittest.mock import Mock

import pytest

from src.chain.chain import ChainId
from src.exceptions.policies import ContentPolicyViolationException
from src.services.moderation import (
    ModerationCheckOrFailService,
    ModerationService,
)


# ----------------------------------------------
# ModerationService
# ----------------------------------------------
def test_is_violating_content_policy():
    ai_api_mock = Mock()
    ai_api_mock.moderation.return_value = True
    chain_id = ChainId("testing-chain-operation")

    service = ModerationService(ai_api_mock)
    service.set_chain_id(chain_id)
    result = service.is_violating_content_policy("text")

    ai_api_mock.moderation.assert_called_once_with("text", "moderation")
    assert result is True


# ----------------------------------------------
# ModerationCheckOrFailService
# ----------------------------------------------
def test_check_moderation_service_success(check_log_message):
    msm = Mock()
    msm.is_violating_content_policy.return_value = False
    chain_id = ChainId("testing-chain-operation")

    service = ModerationCheckOrFailService(msm)
    service.set_chain_id(chain_id)
    result = service.handle("text")

    msm.is_violating_content_policy.assert_called_once_with("text")
    assert result == "text"

    check_log_message(
        "INFO", f"[Authoring] Executing Moderation prompt on {chain_id}"
    )


def test_check_moderation_service_failed(check_log_message):
    msm = Mock()
    msm.is_violating_content_policy.return_value = True
    chain_id = ChainId("testing-chain-operation")

    service = ModerationCheckOrFailService(msm)
    service.set_chain_id(chain_id)
    with pytest.raises(ContentPolicyViolationException):
        service.handle("text")

    check_log_message(
        "INFO", f"[Authoring] Executing Moderation prompt on {chain_id}"
    )

    msm.is_violating_content_policy.assert_called_once_with("text")
