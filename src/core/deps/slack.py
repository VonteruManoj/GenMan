from functools import lru_cache

from src.core.config import get_settings
from src.services.slack import FakeSlackService, SlackService


@lru_cache()
def get_slack_service(channel_id: str = None, token: str = None):
    if (
        channel_id is not None
        and token is not None
        and get_settings().APP_ENV != "testing"
    ):
        return SlackService(channel_id, token)
    return FakeSlackService()
