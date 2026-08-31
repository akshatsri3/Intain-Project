"""
Tests for Reviewer Decision Workflow and AI Suggestions.
"""

from decimal import Decimal
from datetime import date
from app.models.user import User, UserRole
from app.models.loan import Loan, VerificationStatus
from app.models.dataset import Dataset, SourceType, DatasetStatus
from app.models.validation_exception import ValidationException, ExceptionSeverity, ExceptionStatus
from app.models.review_decision import DecisionType
from app.utils.security import hash_password, create_access_token


def test_submit_review_decision_accept(client, db):
    """Reviewer accepting an AI suggestion resolves the exception and verifies clean loans."""
    # Setup reviewer
    reviewer = User(
        name="Reviewer Bob",
        email="rev_test@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.REVIEWER,
    )
    db.add(reviewer)
    db.commit()
    db.refresh(reviewer)
    token = create_access_token({"sub": str(reviewer.id), "role": reviewer.role.value})

    # Dataset & Loan
    dataset = Dataset(
        file_name="rev_test.csv",
        source_type=SourceType.LOAN_TAPE,
        uploaded_by=reviewer.id,
        status=DatasetStatus.COMPLETED,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    loan = Loan(
        dataset_id=dataset.id,
        source_row_number=1,
        loan_id="LN-REV-01",
        original_principal=Decimal("100000.00"),
        current_balance=Decimal("105000.00"),
        verification_status=VerificationStatus.PENDING,
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)

    # Exception
    exc = ValidationException(
        loan_id=loan.id,
        dataset_id=dataset.id,
        rule_code="BALANCE_EXCEEDS_PRINCIPAL",
        severity=ExceptionSeverity.WARNING,
        field_name="current_balance",
        current_value="105000.00",
        expected_range="<= 100000.00",
        message="Balance exceeds principal",
        status=ExceptionStatus.OPEN,
    )
    db.add(exc)
    db.commit()
    db.refresh(exc)

    # Submit decision via API
    resp = client.post(
        f"/reviews/decide/{exc.id}",
        json={
            "decision": "ACCEPT_SUGGESTION",
            "reviewer_note": "Accepted AI suggestion to cap balance",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "ACCEPT_SUGGESTION"

    # Exception should now be resolved
    db.refresh(exc)
    assert exc.status == ExceptionStatus.RESOLVED
    assert exc.resolved_by == reviewer.id

    # Since all exceptions for this loan are now resolved, loan should be VERIFIED
    db.refresh(loan)
    assert loan.verification_status == VerificationStatus.VERIFIED
    assert loan.record_hash is not None


def test_submit_review_decision_reject_loan(client, db):
    """Reviewer rejecting a loan sets status to REJECTED."""
    reviewer = User(
        name="Reviewer Akshat",
        email="rev_akshat@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.REVIEWER,
    )
    db.add(reviewer)
    db.commit()
    db.refresh(reviewer)
    token = create_access_token({"sub": str(reviewer.id), "role": reviewer.role.value})

    dataset = Dataset(
        file_name="rev_test2.csv",
        source_type=SourceType.LOAN_TAPE,
        uploaded_by=reviewer.id,
        status=DatasetStatus.COMPLETED,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    loan = Loan(
        dataset_id=dataset.id,
        source_row_number=1,
        loan_id="LN-REJ-01",
        original_principal=Decimal("50000.00"),
        verification_status=VerificationStatus.PENDING,
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)

    exc = ValidationException(
        loan_id=loan.id,
        dataset_id=dataset.id,
        rule_code="MISSING_DOCUMENT_STATUS",
        severity=ExceptionSeverity.WARNING,
        status=ExceptionStatus.OPEN,
        message="Missing document status",
    )
    db.add(exc)
    db.commit()
    db.refresh(exc)

    resp = client.post(
        f"/reviews/decide/{exc.id}",
        json={
            "decision": "REJECT_LOAN",
            "reviewer_note": "Document not available after custodian check",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    db.refresh(loan)
    assert loan.verification_status == VerificationStatus.REJECTED
