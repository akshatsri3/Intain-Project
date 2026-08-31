from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit_event import AuditEvent


def log_event(
    db: Session,
    entity_type: str,
    entity_id: int,
    event_type: str,
    actor_id: Optional[int] = None,
    actor_role: Optional[str] = None,
    details: Optional[dict] = None,
) -> AuditEvent:
    event = AuditEvent(
        entity_type=entity_type,
        entity_id=entity_id,
        event_type=event_type,
        actor_id=actor_id,
        actor_role=actor_role,
        details_json=details,
    )
    db.add(event)
    return event
