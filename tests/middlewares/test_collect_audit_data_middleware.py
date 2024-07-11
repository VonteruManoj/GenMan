from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient

from src.core.containers import container
from src.main import app
from src.middlewares.collect_audit_data_middleware import (
    collect_audit_data_middleware,
)


def test_collect_audit_data_middleware():
    # Create a new APIRouter for testing
    router = APIRouter()

    # Define the test endpoint
    @router.get(
        "/test_endpoint", dependencies=[Depends(collect_audit_data_middleware)]
    )
    async def test_endpoint():
        return {"message": "This is a test endpoint"}

    # Add the router to the app
    app.include_router(router)

    # Create a TestClient with your FastAPI application
    client = TestClient(app)

    # Send a request to the test endpoint with headers
    response = client.get(
        "/test_endpoint",
        headers={
            "zt-causer-id": "1",
            "zt-causer-type": "user",
            "ZT-Org-Id": "1",
            "ZT-Project-Id": "1",
        },
    )

    assert response.status_code == 200
    data = container.audit_repository().data
    assert data.causer_id == 1
    assert data.causer_type == "user"
    assert data.org_id == 1
    assert data.project_id == 1
