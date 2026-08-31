from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.user import User
from app.models.loan import Loan, VerificationStatus
from app.models.dataset import Dataset
from app.models.validation_exception import ValidationException, ExceptionStatus
from app.schemas.loan import LoanResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("", response_model=List[LoanResponse])
def list_loans(
    search: Optional[str] = None,
    verification_status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Loan)

    if search:
        query = query.filter(
            (Loan.loan_id.ilike(f"%{search}%")) |
            (Loan.borrower_id.ilike(f"%{search}%"))
        )

    if verification_status:
        try:
            vs = VerificationStatus(verification_status)
            query = query.filter(Loan.verification_status == vs)
        except ValueError:
            pass

    return (
        query.order_by(Loan.id)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.get("/summary/global")
def get_global_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_loans = db.query(func.count(Loan.id)).scalar() or 0
    total_datasets = db.query(func.count(Dataset.id)).scalar() or 0
    verified = db.query(func.count(Loan.id)).filter(
        Loan.verification_status == VerificationStatus.VERIFIED).scalar() or 0
    pending = db.query(func.count(Loan.id)).filter(
        Loan.verification_status == VerificationStatus.PENDING).scalar() or 0
    rejected = db.query(func.count(Loan.id)).filter(
        Loan.verification_status == VerificationStatus.REJECTED).scalar() or 0
    open_exceptions = db.query(func.count(ValidationException.id)).filter(
        ValidationException.status == ExceptionStatus.OPEN).scalar() or 0

    quality_score = round((verified / total_loans * 100), 1) if total_loans > 0 else 0.0

    return {
        "total_datasets": total_datasets,
        "total_loans": total_loans,
        "verified": verified,
        "pending": pending,
        "rejected": rejected,
        "open_exceptions": open_exceptions,
        "quality_score": quality_score,
    }
