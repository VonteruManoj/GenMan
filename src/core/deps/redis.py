from typing import AsyncIterator

import redis

from src.core.config import get_settings

from .logger import get_logger


def get_redis_client(url: str, db: int = 1) -> AsyncIterator[redis.Redis]:
    """Attempt to connect to Redis.

    Returns
    -------
    redis.Redis
        Redis client instance.

    Notes
    -----
    If the APP_ENV is set to test, a fake Redis client will be returned.
    """

    try:
        # If the APP_ENV is set to test, return a fake Redis client.
        if get_settings().APP_ENV == "testing":
            session = _get_fake_redis_client()
            get_logger(__name__).debug("[FAKE - Redis] Redis session created")
        else:
            session = _get_redis_client(url, db)
            get_logger(__name__).debug("[Redis] Redis session created")

        # Yield the session to the caller.
        yield session
    finally:
        # Close the session.
        session.close()
        get_logger(__name__).debug("[Redis] Redis session closed")


def _get_redis_client(url: str, db: int = 1) -> redis.Redis:
    return redis.from_url(
        url,
        encoding="utf-8",
        db=db,
        decode_responses=True,
    )


def _get_fake_redis_client() -> redis.Redis:
    from fakeredis import FakeRedis

    return FakeRedis()
