import hashlib
import json
from datetime import datetime, timezone, timedelta, date as date_type
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.loan import Loan, VerificationStatus
from app.models.validation_exception import ValidationException, ExceptionSeverity, ExceptionStatus
from app.models.dataset import Dataset
from app.services.audit_service import log_event

VALID_STATE_CODES = {
    "AP", "AR", "AS", "BR", "CG", "CT", "GA", "GJ", "HR", "HP",
    "JH", "KA", "KL", "MP", "MH", "MN", "ML", "MZ", "NL", "OD",
    "OR", "PB", "RJ", "SK", "TN", "TG", "TS", "TR", "UP", "UK",
    "UT", "WB",
    "AN", "CH", "DH", "DN", "DD", "DL", "JK", "LA", "LD", "PY",
}


def _create_exception(
    db: Session,
    loan: Loan,
    rule_code: str,
    severity: ExceptionSeverity,
    field_name: str,
    current_value: str,
    expected_range: str,
    message: str,
) -> ValidationException:
    exc = ValidationException(
        loan_id=loan.id,
        dataset_id=loan.dataset_id,
        rule_code=rule_code,
        severity=severity,
        field_name=field_name,
        current_value=str(current_value) if current_value is not None else None,
        expected_range=expected_range,
        message=message,
    )
    db.add(exc)
    return exc


def validate_loan(db: Session, loan: Loan) -> List[ValidationException]:
    exceptions = []

    if not loan.loan_id:
        exceptions.append(_create_exception(
            db, loan, "MISSING_LOAN_ID", ExceptionSeverity.WARNING,
            "loan_id", loan.loan_id, "Non-null loan identifier",
            "Loan ID is missing. Record cannot be uniquely identified."
        ))

    if loan.original_principal is None:
        exceptions.append(_create_exception(
            db, loan, "MISSING_PRINCIPAL", ExceptionSeverity.WARNING,
            "original_principal", None, "Non-null positive value",
            "Original principal balance is missing."
        ))

    if not loan.document_status:
        exceptions.append(_create_exception(
            db, loan, "MISSING_DOCUMENT_STATUS", ExceptionSeverity.WARNING,
            "document_status", loan.document_status, "Non-null document status",
            "Document status is not available for this loan."
        ))

    if loan.original_principal is not None and loan.original_principal < 0:
        exceptions.append(_create_exception(
            db, loan, "NEGATIVE_BALANCE", ExceptionSeverity.ERROR,
            "original_principal", str(loan.original_principal), ">= 0",
            f"Original principal is negative: {loan.original_principal}"
        ))
    if loan.current_balance is not None and loan.current_balance < 0:
        exceptions.append(_create_exception(
            db, loan, "NEGATIVE_BALANCE", ExceptionSeverity.ERROR,
            "current_balance", str(loan.current_balance), ">= 0",
            f"Current balance is negative: {loan.current_balance}"
        ))

    if loan.term_months is not None and loan.term_months <= 0:
        exceptions.append(_create_exception(
            db, loan, "NEGATIVE_TERM", ExceptionSeverity.ERROR,
            "term_months", str(loan.term_months), "> 0",
            f"Loan term is non-positive: {loan.term_months} months"
        ))

    if (loan.current_balance is not None and loan.original_principal is not None
            and loan.current_balance > loan.original_principal):
        diff_pct = round(
            float((loan.current_balance - loan.original_principal) / loan.original_principal) * 100, 1
        ) if loan.original_principal > 0 else 0
        exceptions.append(_create_exception(
            db, loan, "BALANCE_EXCEEDS_PRINCIPAL", ExceptionSeverity.WARNING,
            "current_balance", str(loan.current_balance),
            f"<= {loan.original_principal}",
            f"Current balance ({loan.current_balance}) exceeds original principal "
            f"({loan.original_principal}) by {diff_pct}%."
        ))

    if loan.interest_rate is not None:
        if loan.interest_rate < 0:
            exceptions.append(_create_exception(
                db, loan, "RATE_OUT_OF_RANGE", ExceptionSeverity.ERROR,
                "interest_rate", str(loan.interest_rate), "0% to 50%",
                f"Interest rate is negative: {loan.interest_rate}%"
            ))
        elif loan.interest_rate > 50:
            exceptions.append(_create_exception(
                db, loan, "RATE_OUT_OF_RANGE", ExceptionSeverity.ERROR,
                "interest_rate", str(loan.interest_rate), "0% to 50%",
                f"Interest rate is unusually high: {loan.interest_rate}%"
            ))

    if loan.maturity_date and loan.origination_date and loan.maturity_date < loan.origination_date:
        exceptions.append(_create_exception(
            db, loan, "MATURITY_BEFORE_ORIGINATION", ExceptionSeverity.ERROR,
            "maturity_date", str(loan.maturity_date),
            f"After {loan.origination_date}",
            f"Maturity date ({loan.maturity_date}) is before origination date ({loan.origination_date})."
        ))

    if loan.payment_status and loan.days_past_due is not None:
        status_lower = loan.payment_status.lower()
        if "current" in status_lower and loan.days_past_due > 0:
            exceptions.append(_create_exception(
                db, loan, "PAYMENT_STATUS_DPD_MISMATCH", ExceptionSeverity.WARNING,
                "payment_status", f"{loan.payment_status} / DPD={loan.days_past_due}",
                "Current status should have DPD=0",
                f"Payment status is '{loan.payment_status}' but days past due is {loan.days_past_due}."
            ))
        elif ("past due" in status_lower or "delinquent" in status_lower) and loan.days_past_due == 0:
            exceptions.append(_create_exception(
                db, loan, "PAYMENT_STATUS_DPD_MISMATCH", ExceptionSeverity.WARNING,
                "payment_status", f"{loan.payment_status} / DPD={loan.days_past_due}",
                "Past due status should have DPD > 0",
                f"Payment status is '{loan.payment_status}' but days past due is 0."
            ))

    if loan.days_past_due is not None and loan.days_past_due > 360:
        exceptions.append(_create_exception(
            db, loan, "EXCESSIVE_DPD", ExceptionSeverity.WARNING,
            "days_past_due", str(loan.days_past_due), "<= 360",
            f"Days past due ({loan.days_past_due}) exceeds 360."
        ))

    if loan.borrower_state and loan.borrower_state.upper() not in VALID_STATE_CODES:
        exceptions.append(_create_exception(
            db, loan, "INVALID_STATE_CODE", ExceptionSeverity.WARNING,
            "borrower_state", loan.borrower_state, "Valid Indian state/UT code",
            f"'{loan.borrower_state}' is not a recognized Indian state or UT code."
        ))

    if loan.last_updated_at:
        one_year_ago = (datetime.now(timezone.utc) - timedelta(days=365)).date()
        if isinstance(loan.last_updated_at, date_type) and loan.last_updated_at < one_year_ago:
            exceptions.append(_create_exception(
                db, loan, "STALE_RECORD", ExceptionSeverity.WARNING,
                "last_updated_at", str(loan.last_updated_at), f"After {one_year_ago}",
                f"Record was last updated on {loan.last_updated_at}, which is over 1 year ago."
            ))

    if loan.payment_status:
        status_lower = loan.payment_status.lower()
        if any(kw in status_lower for kw in ("closed", "paid off", "paid in full", "settled")):
            if loan.current_balance is not None and loan.current_balance > 0:
                exceptions.append(_create_exception(
                    db, loan, "CLOSED_WITH_BALANCE", ExceptionSeverity.WARNING,
                    "current_balance", str(loan.current_balance), "0 (closed loan)",
                    f"Loan is marked as '{loan.payment_status}' but still has a balance of {loan.current_balance}."
                ))

    return exceptions


def find_duplicates(db: Session, dataset_id: int) -> List[ValidationException]:
    exceptions = []
    loans_in_dataset = db.query(Loan).filter(Loan.dataset_id == dataset_id).all()

    for loan in loans_in_dataset:
        if loan.loan_id:
            dup_count = (
                db.query(func.count(Loan.id))
                .filter(Loan.loan_id == loan.loan_id, Loan.dataset_id != dataset_id)
                .scalar()
            )
            if dup_count > 0:
                exceptions.append(_create_exception(
                    db, loan, "DUPLICATE_LOAN_ID", ExceptionSeverity.WARNING,
                    "loan_id", loan.loan_id,
                    "Unique across datasets",
                    f"Loan ID '{loan.loan_id}' also appears in {dup_count} other dataset(s)."
                ))

        if loan.borrower_id and loan.original_principal and loan.origination_date:
            dup_count = (
                db.query(func.count(Loan.id))
                .filter(
                    Loan.borrower_id == loan.borrower_id,
                    Loan.original_principal == loan.original_principal,
                    Loan.origination_date == loan.origination_date,
                    Loan.id != loan.id,
                )
                .scalar()
            )
            if dup_count > 0:
                exceptions.append(_create_exception(
                    db, loan, "SUSPICIOUS_DUPLICATE", ExceptionSeverity.WARNING,
                    "borrower_id", loan.borrower_id,
                    "Unique borrower+principal+date combination",
                    f"Borrower '{loan.borrower_id}' has {dup_count} other loan(s) with matching principal and date."
                ))

    return exceptions


def compute_record_hash(loan: Loan) -> str:
    canonical = {
        "loan_id": loan.loan_id,
        "borrower_id": loan.borrower_id,
        "loan_type": loan.loan_type,
        "origination_date": str(loan.origination_date) if loan.origination_date else None,
        "maturity_date": str(loan.maturity_date) if loan.maturity_date else None,
        "original_principal": str(loan.original_principal) if loan.original_principal else None,
        "current_balance": str(loan.current_balance) if loan.current_balance else None,
        "interest_rate": str(loan.interest_rate) if loan.interest_rate else None,
        "term_months": loan.term_months,
        "borrower_state": loan.borrower_state,
        "payment_status": loan.payment_status,
        "days_past_due": loan.days_past_due,
        "dataset_id": loan.dataset_id,
        "source_row_number": loan.source_row_number,
    }
    canonical_json = json.dumps(canonical, sort_keys=True, default=str)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def validate_dataset(
    db: Session,
    dataset_id: int,
    actor_id: Optional[int] = None,
    actor_role: Optional[str] = None,
) -> dict:
    db.query(ValidationException).filter(
        ValidationException.dataset_id == dataset_id
    ).delete(synchronize_session=False)
    db.commit()

    db.query(Loan).filter(Loan.dataset_id == dataset_id).update(
        {Loan.verification_status: VerificationStatus.PENDING,
         Loan.verified_by: None, Loan.verified_at: None, Loan.record_hash: None},
        synchronize_session=False,
    )
    db.commit()

    loans = db.query(Loan).filter(Loan.dataset_id == dataset_id).all()
    all_exceptions = []

    for loan in loans:
        excs = validate_loan(db, loan)
        all_exceptions.extend(excs)

    dup_excs = find_duplicates(db, dataset_id)
    all_exceptions.extend(dup_excs)

    db.commit()

    log_event(db, "dataset", dataset_id, "VALIDATION_RUN",
              actor_id=actor_id, actor_role=actor_role,
              details={"exceptions_created": len(all_exceptions)})

    for exc in all_exceptions:
        log_event(db, "exception", exc.id, "EXCEPTION_CREATED",
                  actor_id=actor_id, actor_role=actor_role,
                  details={"rule_code": exc.rule_code, "loan_id": exc.loan_id})

    loan_ids_with_exceptions = set()
    for exc in all_exceptions:
        loan_ids_with_exceptions.add(exc.loan_id)

    auto_verified = 0
    now = datetime.now(timezone.utc)
    for loan in loans:
        if loan.id not in loan_ids_with_exceptions:
            loan.verification_status = VerificationStatus.VERIFIED
            loan.verified_at = now
            loan.record_hash = compute_record_hash(loan)
            auto_verified += 1

            log_event(db, "loan", loan.id, "VERIFIED_RECORD_CREATED",
                      details={"method": "auto_verified", "record_hash": loan.record_hash})

    db.commit()

    return {
        "exceptions_created": len(all_exceptions),
        "loans_auto_verified": auto_verified,
    }
