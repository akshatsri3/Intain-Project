from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from app.database.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)

    # What entity was affected
    entity_type = Column(String(50), nullable=False, index=True)  # loan, dataset, exception
    entity_id = Column(Integer, nullable=False, index=True)

    # What happened
    event_type = Column(String(100), nullable=False, index=True)
    # UPLOADED, IMPORTED, NORMALIZED, VALIDATION_RUN, EXCEPTION_CREATED,
    # AI_SUGGESTION_GENERATED, REVIEWER_COMMENT, FIELD_EDITED,
    # LOAN_APPROVED, LOAN_REJECTED, VERIFIED_RECORD_CREATED, EXPORTED

    # Who did it
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    actor_role = Column(String(50), nullable=True)

    # Event details — JSON blob with event-specific context
    details_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
