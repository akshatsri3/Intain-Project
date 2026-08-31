import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum
from app.database.base import Base


class ExceptionSeverity(str, enum.Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ExceptionStatus(str, enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class ValidationException(Base):
    __tablename__ = "validation_exceptions"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True)

    # What rule was violated
    rule_code = Column(String(100), nullable=False, index=True)
    severity = Column(SAEnum(ExceptionSeverity, native_enum=False), nullable=False)

    # Details
    field_name = Column(String(100), nullable=True)
    current_value = Column(String(500), nullable=True)
    expected_range = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)

    # Resolution
    status = Column(SAEnum(ExceptionStatus, native_enum=False), nullable=False, default=ExceptionStatus.OPEN)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
