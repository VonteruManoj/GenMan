import time

import requests

from src.core.deps.logger import with_logger
from src.schemas.services.config_svc import SearchWidget


@with_logger()
class ConfigSvcRepository:
    CONFIG_SVC_PREFIX = "/config-svc"

    def __init__(self, url: str) -> None:
        self._url = f"{url}{self.CONFIG_SVC_PREFIX}"

    def _get_headers(self, org_id: int) -> dict:
        return {
            "Content-Type": "application/json",
            "X-Org-Id": str(org_id),
        }

    def _handle_failed_call(self, url: str, status_code: int) -> None:
        msg = (
            f"[config-svc] HTTP request `{url}`"
            f" failed with status code: {status_code}"
        )
        self._logger.error(msg)
        raise Exception(msg)

    def get_search_widget_by_deployment_id(
        self, org_id: int, uuid: str
    ) -> SearchWidget | None:
        st = time.time()
        url = f"{self._url}/search-widgets/deployments/{uuid}"
        self._logger.debug(f"[config-svc] Getting connector types from {url}")
        response = requests.get(
            url,
            headers=self._get_headers(org_id=org_id),
        )
        self._logger.debug(
            "[config-svc] Got connector types --- %s seconds ---"
            % (time.time() - st)
        )

        if response.status_code == 200:
            w = SearchWidget(**response.json())
            if not w.active:
                self._logger.warning(
                    f"[config-svc] Widget {uuid} is not active"
                )
                return None
            return w

        self._handle_failed_call(url, response.status_code)
