import json

import pytest
from pydantic import ValidationError

from src.api.v1.endpoints.analytics.requests.semantic_search import (
    AppendEventToBatchRequest,
)


def test_append_event_to_batch_request():
    assert AppendEventToBatchRequest(
        operation="user_click",
        message="User click in a result.",
        data=json.dumps(
            {
                "link": "http://example.com",
                "node_id": 1,
                "project_id": 1,
                "result_order": 2,
                "sort_by": "relevance",
            }
        ),
    )


def test_append_event_to_batch_request_missing_fields():
    with pytest.raises(ValidationError):
        AppendEventToBatchRequest()
