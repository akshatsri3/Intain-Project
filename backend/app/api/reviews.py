from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User, UserRole
from app.models.loan import Loan, VerificationStatus
from app.models.validation_exception import ValidationException, ExceptionStatus
from app.models.review_decision import ReviewDecision, DecisionType
from app.schemas.review import ReviewDecisionRequest, ReviewDecisionResponse
from app.services.ai_suggestion_service import generate_suggestion
from app.services.validation_service import compute_record_hash
from app.services.audit_service import log_event
from app.utils.security import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])


def require_reviewer(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.REVIEWER:
        raise HTTPException(status_code=403, detail="Only REVIEWER can submit review decisions")
    return current_user


@router.post("/decide/{exception_id}", response_model=ReviewDecisionResponse)
def submit_decision(
    exception_id: int,
    request: ReviewDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reviewer),
):
    exc = db.query(ValidationException).filter(ValidationException.id == exception_id).first()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")

    loan = db.query(Loan).filter(Loan.id == exc.loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Associated loan not found")

    ai_suggestion = generate_suggestion(exc, loan)

    decision = ReviewDecision(
        exception_id=exception_id,
        reviewer_id=current_user.id,
        decision=request.decision,
        override_value=request.override_value,
        reviewer_note=request.reviewer_note,
        ai_suggestion_json=request.ai_suggestion_json or ai_suggestion,
    )
    db.add(decision)

    # Update exception status
    exc.status = ExceptionStatus.RESOLVED
    exc.resolved_by = current_user.id
    exc.resolved_at = datetime.now(timezone.utc)
    exc.resolution_note = request.reviewer_note

    db.flush()

    now = datetime.now(timezone.utc)

    if request.decision == DecisionType.ACCEPT_SUGGESTION:
        log_event(db, "exception", exc.id, "AI_SUGGESTION_ACCEPTED",
                  actor_id=current_user.id, actor_role=current_user.role.value,
                  details={"suggestion": ai_suggestion.get("suggested_action")})

    elif request.decision == DecisionType.MANUAL_OVERRIDE:
        log_event(db, "loan", loan.id, "FIELD_EDITED",
                  actor_id=current_user.id, actor_role=current_user.role.value,
                  details={
                      "field": exc.field_name,
                      "old_value": exc.current_value,
                      "new_value": request.override_value,
                      "exception_id": exception_id,
                  })

    elif request.decision == DecisionType.REJECT_LOAN:
        loan.verification_status = VerificationStatus.REJECTED
        log_event(db, "loan", loan.id, "LOAN_REJECTED",
                  actor_id=current_user.id, actor_role=current_user.role.value,
                  details={"reason": request.reviewer_note, "exception_id": exception_id})

    elif request.decision == DecisionType.FLAG_FOR_AUDIT:
        log_event(db, "loan", loan.id, "FLAGGED_FOR_AUDIT",
                  actor_id=current_user.id, actor_role=current_user.role.value,
                  details={"reason": request.reviewer_note, "exception_id": exception_id})

    log_event(db, "exception", exc.id, "REVIEWED",
              actor_id=current_user.id, actor_role=current_user.role.value,
              details={
                  "decision": request.decision.value,
                  "override_value": request.override_value,
                  "note": request.reviewer_note,
              })

    open_exceptions = (
        db.query(ValidationException)
        .filter(
            ValidationException.loan_id == loan.id,
            ValidationException.status == ExceptionStatus.OPEN,
        )
        .count()
    )

    if open_exceptions == 0 and loan.verification_status == VerificationStatus.PENDING:
        loan.verification_status = VerificationStatus.VERIFIED
        loan.verified_by = current_user.id
        loan.verified_at = now
        loan.record_hash = compute_record_hash(loan)

        log_event(db, "loan", loan.id, "VERIFIED_RECORD_CREATED",
                  actor_id=current_user.id, actor_role=current_user.role.value,
                  details={"method": "reviewer_verified", "record_hash": loan.record_hash})

    db.commit()
    db.refresh(decision)
    return decision


@router.get("/pending", response_model=List[ReviewDecisionResponse])
def list_pending_exceptions(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ReviewDecision)
        .order_by(ReviewDecision.decided_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/decisions", response_model=List[ReviewDecisionResponse])
def list_decisions(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ReviewDecision)
        .filter(ReviewDecision.reviewer_id == current_user.id)
        .order_by(ReviewDecision.decided_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
