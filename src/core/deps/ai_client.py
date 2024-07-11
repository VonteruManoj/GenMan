from functools import lru_cache

from src.adapters.ai_api import FakeOpenAIClient, OpenAIClient
from src.core.config import get_settings
from src.repositories.models.usage_log_repository import UsageLogRepository

from .logger import get_logger


@lru_cache()
def get_open_ai_client(
    org_id: str = None,
    api_key: str = None,
    usage_log_repository: UsageLogRepository = None,
):
    env = get_settings().APP_ENV

    if env == "production":
        get_logger(__name__).debug("[OpenAI] Creating client...")
        return OpenAIClient(org_id, api_key, usage_log_repository)

    if env == "testing":
        get_logger(__name__).debug("[FAKE - OpenAI] Creating client...")
        return FakeOpenAIClient(usage_log_repository)

    if org_id is not None and api_key is not None:
        get_logger(__name__).debug("[OpenAI] Creating client...")
        return OpenAIClient(org_id, api_key, usage_log_repository)

    get_logger(__name__).debug("[FAKE - OpenAI] Creating client...")
    return FakeOpenAIClient(usage_log_repository)
