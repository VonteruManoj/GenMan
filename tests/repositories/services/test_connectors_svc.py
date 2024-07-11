from unittest.mock import patch

import pytest

from src.core.containers import container
from src.schemas.services.connectors_svc import Connector, ConnectorType


class TestConnectorsSvc:
    @classmethod
    def setup_class(cls):
        cls.repository = container.connectors_svc_repository()

    @patch("src.repositories.services.connectors_svc.requests.get")
    def test_get_connector_types(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "connectorTypes": [
                {
                    "id": 1,
                    "name": "connector-type-1",
                    "provider": "provider-1",
                    "description": "description-1",
                    "active": True,
                },
                {
                    "id": 2,
                    "name": "connector-type-2",
                    "provider": "provider-2",
                    "description": "description-2",
                    "active": True,
                },
            ]
        }

        cts = self.repository.get_connector_types(org_id=11)

        mock_get.assert_called_once_with(
            "http://connectors-svc/connectors-svc/connector-types",
            headers={"Content-Type": "application/json", "X-Org-Id": "11"},
        )
        assert len(cts) == 2
        assert cts[0].id == 1
        assert cts[1].id == 2

    @patch("src.repositories.services.connectors_svc.requests.get")
    def test_get_connector_types_non_200_fails(self, mock_get):
        mock_get.return_value.status_code = 201

        with pytest.raises(Exception) as e:
            self.repository.get_connector_types(org_id=11)
            assert "HTTP request" in str(e.value)

    @patch("src.repositories.services.connectors_svc.requests.get")
    def test_get_connectors_by_connector_type_id(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "connectors": [
                {
                    "id": 1,
                    "name": "connector-1",
                    "description": "description-1",
                    "active": True,
                },
                {
                    "id": 2,
                    "name": "connector-2",
                    "description": "description-2",
                    "active": True,
                },
            ]
        }

        cs = self.repository.get_connectors_by_connector_type_id(
            org_id=11, type_id=1
        )

        mock_get.assert_called_once_with(
            "http://connectors-svc/connectors-svc"
            "/connectors/connector-types/ids/1",
            headers={"Content-Type": "application/json", "X-Org-Id": "11"},
        )
        assert len(cs) == 2
        assert cs[0].id == 1
        assert cs[0].connector_type is None
        assert cs[1].id == 2
        assert cs[1].connector_type is None

    @patch("src.repositories.services.connectors_svc.requests.get")
    def test_get_connectors_by_connector_type_id_non_200_fails(self, mock_get):
        mock_get.return_value.status_code = 201

        with pytest.raises(Exception) as e:
            self.repository.get_connectors_by_connector_type_id(
                org_id=11, type_id=1
            )
            assert "HTTP request" in str(e.value)

    @patch(
        "src.repositories.services.connectors_svc."
        "ConnectorsSvcRepository.get_connectors_by_connector_type_id"
    )
    @patch(
        "src.repositories.services.connectors_svc."
        "ConnectorsSvcRepository.get_connector_types"
    )
    def test_get_all_connectors(
        self,
        mock_get_connector_types,
        mock_get_connectors_by_connector_type_id,
    ):
        mock_get_connector_types.return_value = [
            ConnectorType(
                id=1,
                name="ct1",
                provider="ct1",
                description="ct1",
                active=False,
            ),
            ConnectorType(
                id=2,
                name="ct2",
                provider="ct2",
                description="ct2",
                active=True,
            ),
        ]

        mock_get_connectors_by_connector_type_id.return_value = [
            Connector(id=1, name="c1", description="c1", active=True),
            Connector(id=2, name="c2", description="c2", active=False),
        ]

        cs = self.repository.get_all_connectors(org_id=11)

        mock_get_connector_types.assert_called_once_with(org_id=11)
        mock_get_connectors_by_connector_type_id.assert_called_once_with(
            org_id=11, type_id=2
        )

        assert len(cs) == 1
        assert cs[0].id == 1
        assert cs[0].connector_type.id == 2
