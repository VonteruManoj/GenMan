from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_get_release():
    response = client.get("ai-service/release")

    assert response.status_code == 200
    assert response.content.decode("utf-8") == "test"
