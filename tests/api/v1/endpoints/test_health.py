from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_get_health(make_success_response_plain):
    response = client.get("ai-service/v1/health")

    assert response.status_code == 200
    assert response.json() == make_success_response_plain(
        status="ok",
        version="v1",
        release="test",  # Default value
    )
