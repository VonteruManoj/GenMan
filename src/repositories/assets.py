from tenacity import retry, stop_after_attempt, wait_random_exponential

from src.contracts.cache import CacheInterface
from src.contracts.repositories.assets import AssetsRepositoryInterface
from src.core.deps.logger import with_logger
from src.util.storage import S3Storage


@with_logger()
class S3CachedAssetsRepository(AssetsRepositoryInterface):
    def __init__(
        self,
        cache: CacheInterface,
        storage: S3Storage,
        bucket: str,
        ttl: float,
    ):
        self._cache = cache
        self._storage = storage
        self._bucket = bucket
        self._ttl = ttl

    def get_json_asset(self, key: str) -> dict:
        """Get JSON asset from cache or S3 bucket

        If asset is not in cache, it will be fetched from S3 bucket and
        stored in cache.

        Parameters
        ----------
        key : str
            Key of the asset

        Returns
        -------
        dict
            JSON asset
        """
        try:
            asset = self._cache.get(key)
        except Exception as e:
            self._logger.warning(
                'Error while getting asset "%s" from cache: %s', key, e
            )
            asset = None

        # If asset is not in cache, fetch it from S3 bucket and store in cache
        if not asset:
            # Get asset from S3 bucket
            @retry(
                reraise=True,
                wait=wait_random_exponential(min=1, max=20),
                stop=stop_after_attempt(3),
            )
            def _get_json_asset(key: str) -> dict:
                return self._storage.get_json(key, self._bucket)

            asset = _get_json_asset(key)

            # Store asset in cache
            try:
                self._cache.set(key, asset, self._ttl)
            except Exception as e:
                self._logger.warning(
                    'Error while setting asset "%s" in cache: %s', key, e
                )
            self._logger.info('Asset "%s" fetched from S3.', key)
        else:
            self._logger.info('Asset "%s" fetched from Redis.', key)

        return asset
