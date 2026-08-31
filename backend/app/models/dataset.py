import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, ForeignKey, BigInteger
from app.database.base import Base


class DatasetStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SourceType(str, enum.Enum):
    LOAN_TAPE = "LOAN_TAPE"
    SERVICER_UPDATE = "SERVICER_UPDATE"
    DOCUMENT_MANIFEST = "DOCUMENT_MANIFEST"
    OTHER = "OTHER"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(500), nullable=False)
    source_type = Column(SAEnum(SourceType, native_enum=False), nullable=False, default=SourceType.OTHER)
    file_size = Column(BigInteger, nullable=True)  # bytes
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    total_rows = Column(Integer, default=0)
    successfully_imported_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    status = Column(SAEnum(DatasetStatus, native_enum=False), nullable=False, default=DatasetStatus.UPLOADED)
