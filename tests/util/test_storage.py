import json
from unittest.mock import Mock, patch

import boto3
import pytest
from moto import mock_aws

from src.util.storage import S3Storage


# ----------------------------------------------
# S3Storage
# ----------------------------------------------
@mock_aws
def test_get_file():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="test-bucket")
    s3.put_object(
        Bucket="test-bucket",
        Key="fake",
        Body=json.dumps({"message": "readme"}),
    )

    s3_storage = S3Storage(s3, "test-bucket")

    assert s3_storage.get_file("fake") == '{"message": "readme"}'


@patch("src.util.storage.S3Storage.get_file")
def test_get_json(mocked_get_file):
    mocked_get_file.return_value = '{"message": "readme"}'

    s3_storage = S3Storage(Mock(), "test-bucket")

    assert s3_storage.get_json("fake") == {"message": "readme"}


def test_get_file_without_bucket_raises_():
    with pytest.raises(ValueError):
        s3_storage = S3Storage(Mock())
        s3_storage.get_file("fake")


@mock_aws
def test_put_file():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="test-bucket")

    s3_storage = S3Storage(s3, "test-bucket")

    s3_storage.put_file("fake", "fake data")

    assert s3_storage.get_file("fake") == "fake data"


@patch("src.util.storage.S3Storage.put_file")
def test_put_json(mocked_put_file):
    s3_storage = S3Storage(Mock(), "test-bucket")

    s3_storage.put_json("fake", {"message": "readme"})

    mocked_put_file.assert_called_once_with(
        "fake", '{"message": "readme"}', None
    )


def test_put_file_without_bucket_raises_():
    with pytest.raises(ValueError):
        s3_storage = S3Storage(Mock())
        s3_storage.put_file("fake", "fake data")


@mock_aws
def test_list_files():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="test-bucket")
    s3.create_bucket(Bucket="fake")
    s3.put_object(Bucket="test-bucket", Key="fake", Body="fake data")
    s3.put_object(Bucket="test-bucket", Key="fake2/fake", Body="fake data 2")

    s3_storage = S3Storage(s3, "test-bucket")

    assert s3_storage.list_files("fake") == []
    assert s3_storage.list_files() == ["fake", "fake2/fake"]
    assert s3_storage.list_files(prefix="fake2") == ["fake2/fake"]


def test_list_files_without_bucket_raises_():
    with pytest.raises(ValueError):
        s3_storage = S3Storage(Mock())
        s3_storage.list_files()
    with pytest.raises(ValueError):
        s3_storage = S3Storage(Mock())
        s3_storage.list_files(prefix="fake2")
