import time

import requests

from src.core.deps.logger import with_logger
from src.schemas.services.connectors_svc import Connector, ConnectorType


@with_logger()
class ConnectorsSvcRepository:
    CONNECTORS_SVC_PREFIX = "/connectors-svc"

    def __init__(self, url: str) -> None:
        self._url = f"{url}{self.CONNECTORS_SVC_PREFIX}"

    def _get_headers(self, org_id: int) -> dict:
        return {
            "Content-Type": "application/json",
            "X-Org-Id": str(org_id),
        }

    def _handle_failed_call(self, url: str, status_code: int) -> None:
        msg = (
            f"[connectors-svc] HTTP request `{url}`"
            f" failed with status code: {status_code}"
        )
        self._logger.error(msg)
        raise Exception(msg)

    def get_connector_types(self, org_id: int) -> list[ConnectorType]:
        st = time.time()
        url = f"{self._url}/connector-types"
        self._logger.debug(
            f"[connectors-svc] Getting connector types from {url}"
        )
        response = requests.get(
            url,
            headers=self._get_headers(org_id=org_id),
        )
        self._logger.debug(
            "[connectors-svc] Got connector types --- %s seconds ---"
            % (time.time() - st)
        )

        if response.status_code == 200:
            return [
                ConnectorType(**o) for o in response.json()["connectorTypes"]
            ]

        self._handle_failed_call(url, response.status_code)

    def get_connectors_by_connector_type_id(
        self, org_id: int, type_id: int
    ) -> list[Connector]:
        st = time.time()
        url = f"{self._url}/connectors/connector-types/ids/{type_id}"
        self._logger.debug(f"[connectors-svc] Getting connectors from {url}")
        response = requests.get(
            url,
            headers=self._get_headers(org_id=org_id),
        )
        self._logger.debug(
            "[connectors-svc] Got connectors --- %s seconds ---"
            % (time.time() - st)
        )
        if response.status_code == 200:
            return [Connector(**o) for o in response.json()["connectors"]]

        self._handle_failed_call(url, response.status_code)

    def get_all_connectors(self, org_id: int) -> list[Connector]:
        try:
            cts = filter(
                lambda t: t.active, self.get_connector_types(org_id=org_id)
            )

            connectors = []
            for ct in cts:
                cs = self.get_connectors_by_connector_type_id(
                    org_id=org_id, type_id=ct.id
                )
                for c in cs:
                    if c.active:
                        c.connector_type = ct
                        connectors.append(c)

        except Exception as e:
            self._logger.error(
                f"[connectors-svc] Error while getting connectors {e}"
            )

            raise e

        return connectors
