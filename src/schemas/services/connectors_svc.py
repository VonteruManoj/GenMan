from pydantic import BaseModel, Field


class ConnectorType(BaseModel):
    id: int
    name: str
    provider: str
    description: str | None
    active: bool


class Connector(BaseModel):
    id: int
    name: str
    description: str | None
    active: bool
    connector_type: ConnectorType | None = Field(default=None)
