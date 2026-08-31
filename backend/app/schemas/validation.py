from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.validation_exception import ExceptionSeverity, ExceptionStatus


class ValidationExceptionResponse(BaseModel):
    id: int
    loan_id: int
    dataset_id: int
    rule_code: str
    severity: ExceptionSeverity
    field_name: Optional[str]
    current_value: Optional[str]
    expected_range: Optional[str]
    message: str
    status: ExceptionStatus
    resolved_by: Optional[int]
    resolved_at: Optional[datetime]
    resolution_note: Optional[str]
    created_at: datetime

    # Loan context — attached when serving exception detail
    loan_loan_id: Optional[str] = None
    loan_borrower_id: Optional[str] = None

    model_config = {"from_attributes": True}


class ValidationExceptionWithSuggestion(ValidationExceptionResponse):
    """Exception response enriched with AI suggestion."""
    ai_suggestion: Optional[dict] = None


class ResolveExceptionRequest(BaseModel):
    status: ExceptionStatus  # RESOLVED or DISMISSED
    resolution_note: Optional[str] = None


class ValidationStatsResponse(BaseModel):
    total: int = 0
    open: int = 0
    resolved: int = 0
    dismissed: int = 0
    errors: int = 0
    warnings: int = 0
    info: int = 0


class ValidationRunResponse(BaseModel):
    dataset_id: int
    exceptions_created: int
    loans_auto_verified: int
    message: str
