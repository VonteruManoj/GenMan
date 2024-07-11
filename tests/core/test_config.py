from src.core.config import Settings


def test_clean_input_validator():
    settings = Settings(APP_NAME='"Test"')

    assert settings.APP_NAME == "Test"
