from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from app.database.base import Base


class ImportError(Base):
    """
    Records rows that could not be imported during CSV ingestion.
    Stored for transparency — no rows are silently dropped.
    """
    __tablename__ = "import_errors"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    error_type = Column(String(100), nullable=False)  # e.g. PARSE_ERROR, MISSING_REQUIRED_FIELD
    error_message = Column(Text, nullable=False)
    raw_data_json = Column(JSON, nullable=True)  # Original row data if available
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
