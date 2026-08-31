from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.audit_event import AuditEvent
from app.schemas.audit import AuditEventResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/trail/{entity_type}/{entity_id}", response_model=List[AuditEventResponse])
def get_audit_trail(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.entity_type == entity_type, AuditEvent.entity_id == entity_id)
        .order_by(AuditEvent.created_at.asc())
        .all()
    )
    return events


@router.get("/recent", response_model=List[AuditEventResponse])
def get_recent_events(
    entity_type: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AuditEvent)

    if entity_type:
        query = query.filter(AuditEvent.entity_type == entity_type)
    if event_type:
        query = query.filter(AuditEvent.event_type == event_type)

    return query.order_by(AuditEvent.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/loan/{loan_id}", response_model=List[AuditEventResponse])
def get_loan_audit_trail(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.entity_type == "loan", AuditEvent.entity_id == loan_id)
        .order_by(AuditEvent.created_at.asc())
        .all()
    )
    return events
