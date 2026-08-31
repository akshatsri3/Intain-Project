import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Date, Text, Enum as SAEnum
from app.database.base import Base


class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)

    # Source lineage — links back to where this record came from
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True)
    source_row_number = Column(Integer, nullable=True)  # Original row in the CSV

    # Loan identifiers
    loan_id = Column(String(100), nullable=True, index=True)
    borrower_id = Column(String(100), nullable=True)

    # Loan characteristics
    loan_type = Column(String(100), nullable=True)
    origination_date = Column(Date, nullable=True)
    maturity_date = Column(Date, nullable=True)
    original_principal = Column(Numeric(15, 2), nullable=True)
    current_balance = Column(Numeric(15, 2), nullable=True)
    interest_rate = Column(Numeric(8, 4), nullable=True)  # Stored as percentage, e.g. 8.5
    term_months = Column(Integer, nullable=True)

    # Borrower info
    borrower_state = Column(String(10), nullable=True)
    loan_purpose = Column(String(100), nullable=True)
    credit_grade = Column(String(20), nullable=True)
    employment_length = Column(String(50), nullable=True)
    income_band = Column(String(50), nullable=True)

    # Payment / servicing
    payment_status = Column(String(50), nullable=True)
    days_past_due = Column(Integer, nullable=True)
    servicer_name = Column(String(255), nullable=True)
    last_payment_date = Column(Date, nullable=True)
    last_updated_at = Column(Date, nullable=True)

    # Document tracking
    document_status = Column(String(100), nullable=True)

    # Source metadata
    source_system = Column(String(100), nullable=True)

    # Processing status
    normalization_status = Column(String(50), nullable=False, default="NORMALIZED")

    # Verification lifecycle
    verification_status = Column(
        SAEnum(VerificationStatus, native_enum=False),
        nullable=False,
        default=VerificationStatus.PENDING,
    )
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    record_hash = Column(String(64), nullable=True)  # SHA-256 of canonical verified record

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
