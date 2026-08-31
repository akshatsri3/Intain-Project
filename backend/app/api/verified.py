import csv
import io
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.user import User, UserRole
from app.models.loan import Loan, VerificationStatus
from app.schemas.loan import LoanResponse, VerifiedLoanStatsResponse
from app.services.audit_service import log_event
from app.utils.security import get_current_user

router = APIRouter(prefix="/verified", tags=["verified"])


@router.get("/loans", response_model=List[LoanResponse])
def list_verified_loans(
    search: Optional[str] = None,
    loan_type: Optional[str] = None,
    borrower_state: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Loan).filter(Loan.verification_status == VerificationStatus.VERIFIED)

    if search:
        query = query.filter(
            (Loan.loan_id.ilike(f"%{search}%")) |
            (Loan.borrower_id.ilike(f"%{search}%"))
        )

    if loan_type:
        query = query.filter(Loan.loan_type.ilike(f"%{loan_type}%"))

    if borrower_state:
        query = query.filter(Loan.borrower_state == borrower_state.upper())

    return query.order_by(Loan.verified_at.desc()).offset(offset).limit(limit).all()


@router.get("/loans/{loan_id}", response_model=LoanResponse)
def get_verified_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.verification_status == VerificationStatus.VERIFIED,
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Verified loan not found")
    return loan


@router.get("/stats", response_model=VerifiedLoanStatsResponse)
def get_verified_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.query(func.count(Loan.id)).scalar() or 0
    verified = db.query(func.count(Loan.id)).filter(
        Loan.verification_status == VerificationStatus.VERIFIED
    ).scalar() or 0
    pending = db.query(func.count(Loan.id)).filter(
        Loan.verification_status == VerificationStatus.PENDING
    ).scalar() or 0
    rejected = db.query(func.count(Loan.id)).filter(
        Loan.verification_status == VerificationStatus.REJECTED
    ).scalar() or 0

    quality_score = round((verified / total * 100), 1) if total > 0 else 0.0

    return VerifiedLoanStatsResponse(
        total_loans=total,
        verified=verified,
        pending=pending,
        rejected=rejected,
        quality_score=quality_score,
    )


@router.get("/export")
def export_verified_loans(
    format: str = Query("csv", pattern="^(csv|json)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    loans = db.query(Loan).filter(
        Loan.verification_status == VerificationStatus.VERIFIED
    ).order_by(Loan.id).all()

    if not loans:
        raise HTTPException(status_code=404, detail="No verified loans to export")

    log_event(db, "dataset", 0, "EXPORTED",
              actor_id=current_user.id, actor_role=current_user.role.value,
              details={"format": format, "record_count": len(loans)})
    db.commit()

    if format == "json":
        data = []
        for loan in loans:
            data.append({
                "id": loan.id,
                "loan_id": loan.loan_id,
                "borrower_id": loan.borrower_id,
                "loan_type": loan.loan_type,
                "origination_date": str(loan.origination_date) if loan.origination_date else None,
                "maturity_date": str(loan.maturity_date) if loan.maturity_date else None,
                "original_principal": float(loan.original_principal) if loan.original_principal else None,
                "current_balance": float(loan.current_balance) if loan.current_balance else None,
                "interest_rate": float(loan.interest_rate) if loan.interest_rate else None,
                "term_months": loan.term_months,
                "borrower_state": loan.borrower_state,
                "loan_purpose": loan.loan_purpose,
                "credit_grade": loan.credit_grade,
                "payment_status": loan.payment_status,
                "days_past_due": loan.days_past_due,
                "servicer_name": loan.servicer_name,
                "document_status": loan.document_status,
                "verification_status": loan.verification_status.value,
                "verified_at": loan.verified_at.isoformat() if loan.verified_at else None,
                "record_hash": loan.record_hash,
                "dataset_id": loan.dataset_id,
                "source_row_number": loan.source_row_number,
            })
        json_str = json.dumps(data, indent=2)
        return StreamingResponse(
            io.BytesIO(json_str.encode()),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=verified_loans.json"},
        )

    # CSV export
    output = io.StringIO()
    fieldnames = [
        "id", "loan_id", "borrower_id", "loan_type", "origination_date",
        "maturity_date", "original_principal", "current_balance", "interest_rate",
        "term_months", "borrower_state", "loan_purpose", "credit_grade",
        "payment_status", "days_past_due", "servicer_name", "document_status",
        "verification_status", "verified_at", "record_hash",
        "dataset_id", "source_row_number",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for loan in loans:
        writer.writerow({
            "id": loan.id,
            "loan_id": loan.loan_id,
            "borrower_id": loan.borrower_id,
            "loan_type": loan.loan_type,
            "origination_date": str(loan.origination_date) if loan.origination_date else "",
            "maturity_date": str(loan.maturity_date) if loan.maturity_date else "",
            "original_principal": str(loan.original_principal) if loan.original_principal else "",
            "current_balance": str(loan.current_balance) if loan.current_balance else "",
            "interest_rate": str(loan.interest_rate) if loan.interest_rate else "",
            "term_months": loan.term_months or "",
            "borrower_state": loan.borrower_state or "",
            "loan_purpose": loan.loan_purpose or "",
            "credit_grade": loan.credit_grade or "",
            "payment_status": loan.payment_status or "",
            "days_past_due": loan.days_past_due if loan.days_past_due is not None else "",
            "servicer_name": loan.servicer_name or "",
            "document_status": loan.document_status or "",
            "verification_status": loan.verification_status.value,
            "verified_at": loan.verified_at.isoformat() if loan.verified_at else "",
            "record_hash": loan.record_hash or "",
            "dataset_id": loan.dataset_id,
            "source_row_number": loan.source_row_number or "",
        })

    csv_bytes = output.getvalue().encode()
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=verified_loans.csv"},
    )
