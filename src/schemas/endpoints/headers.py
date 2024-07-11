from typing import Optional

from fastapi import Header


class AuditDataHeaders:
    def __init__(
        self,
        zt_causer_id: Optional[int] = Header(
            alias="zt-causer-id", examples=[1]
        ),
        zt_causer_type: Optional[str] = Header(
            alias="zt-causer-type", examples=["App\\Models\\User"]
        ),
        zt_org_id: Optional[int] = Header(
            default=None, alias="zt-org-id", examples=[1]
        ),
        x_org_id: Optional[int] = Header(
            default=None, alias="x-org-id", examples=[1]
        ),
        zt_project_id: Optional[int] = Header(
            default=None, alias="zt-project-id", examples=[1]
        ),
    ):
        self.zt_causer_id = zt_causer_id
        self.zt_causer_type = zt_causer_type
        self.zt_org_id = x_org_id or zt_org_id
        self.zt_project_id = zt_project_id

    def to_dict(self):
        return {
            "zt_causer_id": (self.zt_causer_id),
            "zt_causer_type": (self.zt_causer_type),
            "zt_org_id": (self.zt_org_id),
            "zt_project_id": (self.zt_project_id),
        }
