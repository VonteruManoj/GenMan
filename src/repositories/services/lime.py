import time

import requests

from src.core.deps.logger import with_logger


@with_logger()
class LimeRepository:
    CONFIG_SVC_PREFIX = "/api/v2"

    def __init__(self, url: str, key: str) -> None:
        self._url = f"{url}{self.CONFIG_SVC_PREFIX}"
        self._key = key

    def _get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "x-api-key": str(self._key),
        }

    def _handle_failed_call(self, url: str, status_code: int) -> None:
        msg = (
            f"[lime] HTTP request `{url}`"
            f" failed with status code: {status_code}"
        )
        self._logger.error(msg)
        raise Exception(msg)

    def get_agent_tags(self, id: int) -> list[str]:
        st = time.time()
        url = f"{self._url}/agent/profile/{id}/tags"
        self._logger.debug(f"[lime] Getting agent tags `{url}`")
        response = requests.get(
            url,
            headers=self._get_headers(),
        )
        self._logger.debug(
            "[lime] Got tags response --- %s seconds ---" % (time.time() - st)
        )

        if response.status_code == 200:
            return response.json()["data"]

        self._handle_failed_call(url, response.status_code)
