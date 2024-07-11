from fastapi import Depends

from src.core.containers import container
from src.schemas.endpoints.headers import AuditDataHeaders


async def collect_audit_data_middleware(headers: AuditDataHeaders = Depends()):
    audit_repository = container.audit_repository()
    audit_repository.set_from_headers(headers)
