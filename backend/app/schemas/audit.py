from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    event_type: str
    actor_id: Optional[int]
    actor_role: Optional[str]
    details_json: Optional[dict]
    created_at: datetime

    model_config = {"from_attributes": True}
