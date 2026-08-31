from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel


class LoanResponse(BaseModel):
    id: int
    dataset_id: int
    source_row_number: Optional[int]
    loan_id: Optional[str]
    borrower_id: Optional[str]
    loan_type: Optional[str]
    origination_date: Optional[date]
    maturity_date: Optional[date]
    original_principal: Optional[Decimal]
    current_balance: Optional[Decimal]
    interest_rate: Optional[Decimal]
    term_months: Optional[int]
    borrower_state: Optional[str]
    loan_purpose: Optional[str]
    credit_grade: Optional[str]
    employment_length: Optional[str]
    income_band: Optional[str]
    payment_status: Optional[str]
    days_past_due: Optional[int]
    servicer_name: Optional[str]
    last_payment_date: Optional[date]
    document_status: Optional[str]
    normalization_status: str
    verification_status: str = "PENDING"
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    record_hash: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class VerifiedLoanStatsResponse(BaseModel):
    total_loans: int = 0
    verified: int = 0
    pending: int = 0
    rejected: int = 0
    quality_score: float = 0.0  # percentage of verified / total

