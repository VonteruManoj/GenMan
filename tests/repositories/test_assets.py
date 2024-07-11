from unittest.mock import patch

from moto import mock_aws

from src.core.config import get_settings
from src.core.containers import Container
from src.core.deps.boto3 import get_client


# ----------------------------------------------
# AssetsRepository
# ----------------------------------------------
@mock_aws
def test_get_json_asset_uses_cache_write_writethrough(check_log_message):
    container = Container()
    container.config.from_pydantic(get_settings())
    assets_repository = container.assets_s3_cached_repository()

    s3_storage = container.storage_s3()
    s3_storage._client.create_bucket(Bucket="fake-ai-service-assets")
    s3_storage.put_json(
        "fake", {"message": "readme"}, "fake-ai-service-assets"
    )

    assert assets_repository.get_json_asset("fake") == {"message": "readme"}
    check_log_message(
        "INFO",
        'Asset "fake" fetched from S3.',
    )
    assert assets_repository._cache.get("fake") == {"message": "readme"}

    with patch.object(
        assets_repository._storage, "get_json", return_value=None
    ) as mock_method:
        asset = assets_repository.get_json_asset("fake")
        assert mock_method.call_count == 0

    assert asset == {"message": "readme"}
    check_log_message(
        "INFO",
        'Asset "fake" fetched from Redis.',
    )

    get_client.cache_clear()


@mock_aws
def test_get_json_asset_doesnt_depends_on_cache(check_log_message):
    container = Container()
    container.config.from_pydantic(get_settings())
    assets_repository = container.assets_s3_cached_repository()

    s3_storage = container.storage_s3()
    s3_storage._client.create_bucket(Bucket="fake-ai-service-assets")
    s3_storage.put_json(
        "fake", {"message": "readme"}, "fake-ai-service-assets"
    )

    with patch.object(
        assets_repository._cache,
        "get",
        side_effect=Exception("Cache GET is down"),
    ), patch.object(
        assets_repository._cache,
        "set",
        side_effect=Exception("Cache SET is down"),
    ):
        assert assets_repository.get_json_asset("fake") == {
            "message": "readme"
        }

    check_log_message(
        "INFO",
        'Asset "fake" fetched from S3.',
    )
    check_log_message(
        "WARNING",
        'Error while getting asset "fake" from cache: Cache GET is down',
    )
    check_log_message(
        "WARNING",
        'Error while setting asset "fake" in cache: Cache SET is down',
    )

    get_client.cache_clear()
