import contextlib

from src.core.config import get_settings


# ----------------------------------------------
# Settings
# ----------------------------------------------
@contextlib.contextmanager
def override_settings(**overrides):
    settings = get_settings()
    original = {}

    try:
        for key, value in overrides.items():
            original[key] = getattr(settings, key)
            setattr(settings, key, value)

        yield
    finally:
        for key, value in original.items():
            setattr(settings, key, value)
