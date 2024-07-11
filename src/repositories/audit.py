from src.schemas.endpoints.headers import AuditDataHeaders


class AuditData:
    def __init__(
        self,
        user_id: int = None,
        causer_id: int = None,
        causer_type: str = None,
        org_id: int = None,
        project_id: int = None,
    ):
        self.user_id = user_id
        self.causer_id = causer_id
        self.causer_type = causer_type
        self.org_id = org_id
        self.project_id = project_id


class AuditInMemoryRepository:
    def __init__(self):
        self.data = AuditData()

    def set_from_metadata(self, meta: dict):
        self.data.user_id = meta.get("user_id", None)
        self.data.org_id = meta.get("org_id", None)
        self.data.project_id = meta.get("project_id", None)

    def set_from_headers(self, headers: AuditDataHeaders):
        self.data.causer_id = headers.zt_causer_id
        self.data.causer_type = headers.zt_causer_type
        self.data.org_id = headers.zt_org_id
        self.data.project_id = headers.zt_project_id

    def is_agent(self):
        return self.data.causer_type == "App\\Models\\Agent"
