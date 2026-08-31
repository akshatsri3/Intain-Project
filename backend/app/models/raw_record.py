from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from app.database.base import Base


class RawRecord(Base):
    """
    Stores the original CSV row exactly as received, before any normalization.
    This is never modified after creation — it is the ground truth source record.
    """
    __tablename__ = "raw_records"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)  # 1-based row number in the original CSV
    raw_data_json = Column(JSON, nullable=False)  # Original CSV row as key-value dict
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
