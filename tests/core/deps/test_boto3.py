from unittest import mock
from unittest.mock import Mock

import pytest

from src.core.deps.boto3 import get_client, get_session

variations = [
    (
        "test",
        {
            "aws_access_key_id": None,
            "aws_secret_access_key": None,
            "region_name": "us-east-1",
        },
        {
            "aws_access_key_id": None,
            "aws_secret_access_key": None,
            "region_name": "us-east-1",
        },
    ),
    (
        "test",
        {
            "aws_access_key_id": "aws_access_key_id",
            "aws_secret_access_key": None,
            "region_name": "us-east-1",
        },
        {
            "aws_access_key_id": "aws_access_key_id",
            "aws_secret_access_key": None,
            "region_name": "us-east-1",
        },
    ),
    (
        "test",
        {
            "aws_access_key_id": "aws_access_key_id",
            "aws_secret_access_key": "aws_secret_access_key",
            "region_name": "us-east-1",
        },
        {
            "aws_access_key_id": "aws_access_key_id",
            "aws_secret_access_key": "aws_secret_access_key",
            "region_name": "us-east-1",
        },
    ),
    (
        "local",
        {
            "aws_access_key_id": None,
            "aws_secret_access_key": None,
            "region_name": "us-east-1",
        },
        {
            "aws_access_key_id": "fake-key-id",
            "aws_secret_access_key": "fake-access-key",
            "region_name": "us-east-1",
            "endpoint_url": "http://local-aws:4566",
        },
    ),
    (
        "local",
        {
            "aws_access_key_id": "aws_access_key_id",
            "aws_secret_access_key": None,
            "region_name": "us-east-1",
        },
        {
            "aws_access_key_id": "fake-key-id",
            "aws_secret_access_key": "fake-access-key",
            "region_name": "us-east-1",
            "endpoint_url": "http://local-aws:4566",
        },
    ),
    (
        "local",
        {
            "aws_access_key_id": "aws_access_key_id",
            "aws_secret_access_key": "aws_secret_access_key",
            "region_name": "us-east-1",
        },
        {
            "aws_access_key_id": "aws_access_key_id",
            "aws_secret_access_key": "aws_secret_access_key",
            "region_name": "us-east-1",
        },
    ),
]


@pytest.mark.parametrize(("env", "params", "results"), variations)
@mock.patch("src.core.deps.boto3.boto3.session.Session")
def test_get_session(Session_mock, override_settings, env, params, results):
    with override_settings(APP_ENV=env):
        get_session(**params)

    Session_mock.assert_called_once_with(
        aws_access_key_id=results["aws_access_key_id"],
        aws_secret_access_key=results["aws_secret_access_key"],
        region_name=results["region_name"],
    )

    get_session.cache_clear()


@pytest.mark.parametrize(("env", "params", "results"), variations)
def test_get_s3_client(
    override_settings, env, params, results, check_log_message
):
    session_mock = Mock()

    with override_settings(APP_ENV=env), override_settings(
        AWS_ACCESS_KEY_ID=params["aws_access_key_id"]
    ), override_settings(
        AWS_SECRET_ACCESS_KEY=params["aws_secret_access_key"]
    ), override_settings(
        AWS_DEFAULT_REGION=params["region_name"]
    ):
        get_client(session_mock, "s3")

    if env == "local" and results.get("endpoint_url"):
        session_mock.client.assert_called_once_with(
            service_name="s3", endpoint_url=results["endpoint_url"]
        )
        check_log_message("DEBUG", "[LocalStack] s3 mocked in local")
    else:
        session_mock.client.assert_called_once_with(service_name="s3")
        check_log_message("DEBUG", "[AWS] s3 client created")

    get_client.cache_clear()
