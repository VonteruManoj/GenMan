from unittest.mock import patch

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from src.main import app, container
from src.models.usage_log import UsageLog
from src.util.storage import S3Storage

client = TestClient(app)


#################################################
# Metadata/Information
#################################################
@mock_aws
def test_get_metadata(make_prompt_templates_plain):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="fake-ai-service-assets")
    s3.put_json(
        "prompt_templates.json",
        make_prompt_templates_plain(),
        "fake-ai-service-assets",
    )

    response = client.get("ai-service/v1/authoring")

    assert response.status_code == 200
    assert response.json() == {
        "error": False,
        "error_code": None,
        "message": None,
        "data": {
            "ChangeTone": {"max_tokens": 160, "disabled": False},
            "FixGrammar": {"max_tokens": 160, "disabled": False},
            "Summarize": {"max_tokens": 160, "disabled": False},
            "SummarizeIntoSteps": {"max_tokens": 160, "disabled": False},
            "ImproveWriting": {"max_tokens": 160, "disabled": False},
            "Translate": {"max_tokens": 160, "disabled": False},
            "ReduceReadingComplexity": {"max_tokens": 160, "disabled": False},
            "ReduceReadingTime": {"max_tokens": 160, "disabled": False},
            "ExpandWriting": {"max_tokens": 160, "disabled": False},
        },
    }

    assert len(response.json()["data"]) == len(make_prompt_templates_plain())


#################################################
# Prompts
#################################################
@mock_aws
@pytest.mark.usefixtures("refresh_database")
def test_post_fix_grammar(
    make_prompt_templates_plain, make_success_response_plain
):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="fake-ai-service-assets")
    s3.put_json(
        "prompt_templates.json",
        make_prompt_templates_plain(),
        "fake-ai-service-assets",
    )

    response = client.post(
        "ai-service/v1/authoring/fix-grammar",
        json={
            "text": "Hello, world!",
            "metadata": {"user_id": 1, "org_id": 2, "project_id": 3},
        },
    )

    assert response.status_code == 200
    assert response.json() == make_success_response_plain(
        text="This is a completion fake response, prompt:"
        " Fix spelling and grammatical errors, ignore"
        ' words between "#":\n\nHello, world!'
    )

    with container.db().session() as session:
        assert session.query(UsageLog).count() == 2


@mock_aws
@pytest.mark.usefixtures("refresh_database")
def test_post_summarize(make_prompt_templates_plain):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="fake-ai-service-assets")
    s3.put_json(
        "prompt_templates.json",
        make_prompt_templates_plain(),
        "fake-ai-service-assets",
    )

    response = client.post(
        "ai-service/v1/authoring/summarize",
        json={
            "text": "Hello, world!",
            "metadata": {"user_id": 1, "org_id": 2, "project_id": 3},
        },
    )

    assert response.status_code == 200
    assert (
        "This is a chat completion fake response"
        in response.json()["data"]["text"]
    )
    assert "Hello, world!" in response.json()["data"]["text"]

    with container.db().session() as session:
        assert session.query(UsageLog).count() == 2


@mock_aws
@pytest.mark.usefixtures("refresh_database")
def test_post_summarize_into_steps(make_prompt_templates_plain):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="fake-ai-service-assets")
    s3.put_json(
        "prompt_templates.json",
        make_prompt_templates_plain(),
        "fake-ai-service-assets",
    )

    response = client.post(
        "ai-service/v1/authoring/summarize-into-steps",
        json={
            "text": "Hello, world!",
            "metadata": {"user_id": 1, "org_id": 2, "project_id": 3},
        },
    )

    assert response.status_code == 200
    assert (
        "This is a chat completion fake response"
        in response.json()["data"]["text"]
    )
    assert "Hello, world!" in response.json()["data"]["text"]

    with container.db().session() as session:
        assert session.query(UsageLog).count() == 2


@mock_aws
@pytest.mark.usefixtures("refresh_database")
def test_post_change_tone(make_prompt_templates_plain):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="fake-ai-service-assets")
    s3.put_json(
        "prompt_templates.json",
        make_prompt_templates_plain(),
        "fake-ai-service-assets",
    )

    response = client.post(
        "ai-service/v1/authoring/change-tone",
        json={
            "text": "Hello, world!",
            "tone": "friendly",
            "metadata": {"user_id": 1, "org_id": 2, "project_id": 3},
        },
    )

    assert response.status_code == 200
    assert (
        "This is a chat completion fake response"
        in response.json()["data"]["text"]
    )
    assert "Hello, world!" in response.json()["data"]["text"]

    with container.db().session() as session:
        assert session.query(UsageLog).count() == 2


@mock_aws
@pytest.mark.usefixtures("refresh_database")
def test_translate(make_prompt_templates_plain):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="fake-ai-service-assets")
    s3.put_json(
        "prompt_templates.json",
        make_prompt_templates_plain(),
        "fake-ai-service-assets",
    )

    response = client.post(
        "ai-service/v1/authoring/translate",
        json={
            "text": "Hello, world!",
            "language": "italian",
            "metadata": {"user_id": 1, "org_id": 2, "project_id": 3},
        },
    )

    assert response.status_code == 200
    assert (
        "This is a chat completion fake response"
        in response.json()["data"]["text"]
    )
    assert "Hello, world!" in response.json()["data"]["text"]

    with container.db().session() as session:
        assert session.query(UsageLog).count() == 2


@mock_aws
@pytest.mark.usefixtures("refresh_database")
def test_improve_writing(make_prompt_templates_plain):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="fake-ai-service-assets")
    s3.put_json(
        "prompt_templates.json",
        make_prompt_templates_plain(),
        "fake-ai-service-assets",
    )

    response = client.post(
        "ai-service/v1/authoring/improve-writing",
        json={
            "text": "Hello, world!",
            "metadata": {"user_id": 1, "org_id": 2, "project_id": 3},
        },
    )

    assert response.status_code == 200
    assert (
        "This is a chat completion fake response"
        in response.json()["data"]["text"]
    )
    assert "Hello, world!" in response.json()["data"]["text"]

    with container.db().session() as session:
        assert session.query(UsageLog).count() == 2


@mock_aws
@pytest.mark.usefixtures("refresh_database")
def test_reduce_reading_complexity(make_prompt_templates_plain):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="fake-ai-service-assets")
    s3.put_json(
        "prompt_templates.json",
        make_prompt_templates_plain(),
        "fake-ai-service-assets",
    )

    response = client.post(
        "ai-service/v1/authoring/reduce-reading-complexity",
        json={
            "text": "Hello, world!",
            "metadata": {"user_id": 1, "org_id": 2, "project_id": 3},
        },
    )

    assert response.status_code == 200
    assert (
        "This is a chat completion fake response"
        in response.json()["data"]["text"]
    )
    assert "Hello, world!" in response.json()["data"]["text"]

    with container.db().session() as session:
        assert session.query(UsageLog).count() == 2


@mock_aws
@pytest.mark.usefixtures("refresh_database")
def test_reduce_reading_time(make_prompt_templates_plain):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="fake-ai-service-assets")
    s3.put_json(
        "prompt_templates.json",
        make_prompt_templates_plain(),
        "fake-ai-service-assets",
    )

    response = client.post(
        "ai-service/v1/authoring/reduce-reading-time",
        json={
            "text": "Hello, world!",
            "metadata": {"user_id": 1, "org_id": 2, "project_id": 3},
        },
    )

    assert response.status_code == 200
    assert (
        "This is a chat completion fake response"
        in response.json()["data"]["text"]
    )
    assert "Hello, world!" in response.json()["data"]["text"]

    with container.db().session() as session:
        assert session.query(UsageLog).count() == 2


@mock_aws
@pytest.mark.usefixtures("refresh_database")
def test_expand_writing(make_prompt_templates_plain):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="fake-ai-service-assets")
    s3.put_json(
        "prompt_templates.json",
        make_prompt_templates_plain(),
        "fake-ai-service-assets",
    )

    response = client.post(
        "ai-service/v1/authoring/expand-writing",
        json={
            "text": "Hello, world!",
            "metadata": {"user_id": 1, "org_id": 2, "project_id": 3},
        },
    )

    assert response.status_code == 200
    assert (
        "This is a chat completion fake response"
        in response.json()["data"]["text"]
    )
    assert "Hello, world!" in response.json()["data"]["text"]

    with container.db().session() as session:
        assert session.query(UsageLog).count() == 2


#################################################
# Prompts failed due to moderation
#################################################
prompt_calls = [
    ("change-tone", {"text": "Hello, world!", "tone": "friendly"}),
    ("summarize", {"text": "Hello, world!"}),
    ("summarize-into-steps", {"text": "Hello, world!"}),
    ("fix-grammar", {"text": "Hello, world!"}),
    ("translate", {"text": "Hello, world!", "language": "italian"}),
    ("improve-writing", {"text": "Hello, world!"}),
    ("reduce-reading-complexity", {"text": "Hello, world!"}),
    ("reduce-reading-time", {"text": "Hello, world!"}),
    ("expand-writing", {"text": "Hello, world!"}),
]


@patch("src.adapters.ai_api.FakeOpenAIClient.moderation")
@pytest.mark.parametrize(("append", "params"), prompt_calls)
@mock_aws
def test_for_all_input_rows(
    moderation_mock, make_prompt_templates_plain, append: str, params: dict
):
    moderation_mock.return_value = True

    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="fake-ai-service-assets")
    s3.put_json(
        "prompt_templates.json",
        make_prompt_templates_plain(),
        "fake-ai-service-assets",
    )

    response = client.post(
        f"ai-service/v1/authoring/{append}",
        json={
            **params,
            "metadata": {"user_id": 1, "org_id": 2, "project_id": 3},
        },
    )

    assert response.status_code == 200
    assert response.json()["error"] is True
    assert response.json()["error_code"] == 4019
    assert (
        response.json()["message"]
        == "The given text is flagged as violating content policy."
    )
