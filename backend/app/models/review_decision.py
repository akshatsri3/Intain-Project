import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum as SAEnum
from app.database.base import Base


class DecisionType(str, enum.Enum):
    ACCEPT_SUGGESTION = "ACCEPT_SUGGESTION"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"
    REJECT_LOAN = "REJECT_LOAN"
    FLAG_FOR_AUDIT = "FLAG_FOR_AUDIT"


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id = Column(Integer, primary_key=True, index=True)
    exception_id = Column(Integer, ForeignKey("validation_exceptions.id"), nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Decision
    decision = Column(SAEnum(DecisionType, native_enum=False), nullable=False)
    override_value = Column(String(500), nullable=True)  # Manual correction value
    reviewer_note = Column(Text, nullable=True)

    # AI context — what suggestion was shown when the decision was made
    ai_suggestion_json = Column(JSON, nullable=True)

    decided_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
