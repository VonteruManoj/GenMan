import pytest
from pydantic import ValidationError

from src.api.v1.endpoints.responses.health import HealthData, HealthResponse


def test_health_response():
    assert HealthResponse(
        data=HealthData(status="Turn every huan into an expert.")
    )


def test_health_response_missing_fields():
    with pytest.raises(ValidationError):
        HealthResponse()
