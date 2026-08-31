from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.user import User, UserRole
from app.models.loan import Loan
from app.models.validation_exception import ValidationException, ExceptionSeverity, ExceptionStatus
from app.schemas.validation import (
    ValidationExceptionResponse,
    ValidationExceptionWithSuggestion,
    ResolveExceptionRequest,
    ValidationStatsResponse,
    ValidationRunResponse,
)
from app.services.validation_service import validate_dataset
from app.services.ai_suggestion_service import generate_suggestion, generate_batch_summary
from app.services.audit_service import log_event
from app.utils.security import get_current_user

router = APIRouter(prefix="/validation", tags=["validation"])


def require_operator(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.DATA_OPERATOR:
        raise HTTPException(status_code=403, detail="Only DATA_OPERATOR can run validation")
    return current_user


def require_reviewer(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.REVIEWER:
        raise HTTPException(status_code=403, detail="Only REVIEWER can manage exceptions")
    return current_user


@router.post("/run/{dataset_id}", response_model=ValidationRunResponse)
def run_validation(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    result = validate_dataset(db, dataset_id, actor_id=current_user.id, actor_role=current_user.role.value)
    return ValidationRunResponse(
        dataset_id=dataset_id,
        exceptions_created=result["exceptions_created"],
        loans_auto_verified=result["loans_auto_verified"],
        message=f"Validation complete. {result['exceptions_created']} exceptions found, "
                f"{result['loans_auto_verified']} loans auto-verified.",
    )


@router.get("/exceptions", response_model=List[ValidationExceptionWithSuggestion])
def list_exceptions(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = None,
    rule_code: Optional[str] = None,
    search: Optional[str] = None,
    dataset_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ValidationException)

    if status_filter:
        try:
            query = query.filter(ValidationException.status == ExceptionStatus(status_filter))
        except ValueError:
            pass

    if severity:
        try:
            query = query.filter(ValidationException.severity == ExceptionSeverity(severity))
        except ValueError:
            pass

    if rule_code:
        query = query.filter(ValidationException.rule_code == rule_code)

    if dataset_id:
        query = query.filter(ValidationException.dataset_id == dataset_id)

    if search:
        matching_loan_ids = (
            db.query(Loan.id)
            .filter(
                (Loan.loan_id.ilike(f"%{search}%")) |
                (Loan.borrower_id.ilike(f"%{search}%"))
            )
            .subquery()
        )
        query = query.filter(ValidationException.loan_id.in_(matching_loan_ids))

    exceptions = (
        query.order_by(ValidationException.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    results = []
    for exc in exceptions:
        loan = db.query(Loan).filter(Loan.id == exc.loan_id).first()
        suggestion = generate_suggestion(exc, loan)

        result = ValidationExceptionWithSuggestion.model_validate(exc)
        result.ai_suggestion = suggestion
        if loan:
            result.loan_loan_id = loan.loan_id
            result.loan_borrower_id = loan.borrower_id
        results.append(result)

    return results


@router.get("/exceptions/{exception_id}", response_model=ValidationExceptionWithSuggestion)
def get_exception(
    exception_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exc = db.query(ValidationException).filter(ValidationException.id == exception_id).first()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")

    loan = db.query(Loan).filter(Loan.id == exc.loan_id).first()
    suggestion = generate_suggestion(exc, loan)

    result = ValidationExceptionWithSuggestion.model_validate(exc)
    result.ai_suggestion = suggestion
    if loan:
        result.loan_loan_id = loan.loan_id
        result.loan_borrower_id = loan.borrower_id

    log_event(db, "exception", exc.id, "AI_SUGGESTION_GENERATED",
              actor_id=current_user.id, actor_role=current_user.role.value,
              details={"suggestion": suggestion})
    db.commit()

    return result


@router.get("/stats", response_model=ValidationStatsResponse)
def get_validation_stats(
    dataset_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ValidationException)
    if dataset_id:
        query = query.filter(ValidationException.dataset_id == dataset_id)

    total = query.count()
    open_count = query.filter(ValidationException.status == ExceptionStatus.OPEN).count()
    resolved = query.filter(ValidationException.status == ExceptionStatus.RESOLVED).count()
    dismissed = query.filter(ValidationException.status == ExceptionStatus.DISMISSED).count()
    errors = query.filter(ValidationException.severity == ExceptionSeverity.ERROR).count()
    warnings = query.filter(ValidationException.severity == ExceptionSeverity.WARNING).count()
    info = query.filter(ValidationException.severity == ExceptionSeverity.INFO).count()

    return ValidationStatsResponse(
        total=total, open=open_count, resolved=resolved, dismissed=dismissed,
        errors=errors, warnings=warnings, info=info,
    )


@router.patch("/exceptions/{exception_id}", response_model=ValidationExceptionResponse)
def resolve_exception(
    exception_id: int,
    request: ResolveExceptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reviewer),
):
    exc = db.query(ValidationException).filter(ValidationException.id == exception_id).first()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")

    exc.status = request.status
    exc.resolved_by = current_user.id
    exc.resolved_at = datetime.now(timezone.utc)
    exc.resolution_note = request.resolution_note

    log_event(db, "exception", exc.id, "EXCEPTION_RESOLVED",
              actor_id=current_user.id, actor_role=current_user.role.value,
              details={"new_status": request.status.value, "note": request.resolution_note})

    db.commit()
    db.refresh(exc)
    return exc


@router.get("/batch-summary")
def get_batch_summary(
    dataset_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ValidationException)
    if dataset_id:
        query = query.filter(ValidationException.dataset_id == dataset_id)

    exceptions = query.all()
    return generate_batch_summary(exceptions)
