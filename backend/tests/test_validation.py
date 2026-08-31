"""
Tests for Validation Engine and Duplicate Detection.
"""

from decimal import Decimal
from datetime import date
from app.models.loan import Loan, VerificationStatus
from app.models.dataset import Dataset, SourceType, DatasetStatus
from app.models.validation_exception import ValidationException, ExceptionSeverity, ExceptionStatus
from app.services.validation_service import validate_loan, find_duplicates, validate_dataset


def test_validate_loan_clean(db):
    """Clean loan should produce 0 exceptions."""
    loan = Loan(
        dataset_id=1,
        source_row_number=1,
        loan_id="LN-TEST-01",
        borrower_id="BR-001",
        loan_type="Mortgage",
        origination_date=date(2022, 1, 1),
        maturity_date=date(2052, 1, 1),
        original_principal=Decimal("500000.00"),
        current_balance=Decimal("450000.00"),
        interest_rate=Decimal("6.5000"),
        term_months=360,
        borrower_state="MH",
        payment_status="Current",
        days_past_due=0,
        document_status="Complete",
    )
    exceptions = validate_loan(db, loan)
    assert len(exceptions) == 0


def test_validate_balance_exceeds_principal(db):
    """Balance > Principal should trigger BALANCE_EXCEEDS_PRINCIPAL exception."""
    loan = Loan(
        dataset_id=1,
        source_row_number=2,
        loan_id="LN-TEST-02",
        original_principal=Decimal("100000.00"),
        current_balance=Decimal("120000.00"),
        document_status="Complete",
    )
    exceptions = validate_loan(db, loan)
    codes = [e.rule_code for e in exceptions]
    assert "BALANCE_EXCEEDS_PRINCIPAL" in codes


def test_validate_negative_balance_and_term(db):
    """Negative balance and non-positive term should trigger ERRORs."""
    loan = Loan(
        dataset_id=1,
        source_row_number=3,
        loan_id="LN-TEST-03",
        original_principal=Decimal("-5000.00"),
        current_balance=Decimal("-2000.00"),
        term_months=0,
        document_status="Complete",
    )
    exceptions = validate_loan(db, loan)
    codes = [e.rule_code for e in exceptions]
    assert "NEGATIVE_BALANCE" in codes
    assert "NEGATIVE_TERM" in codes


def test_validate_dates_and_rates(db):
    """Maturity before origination and high interest rate."""
    loan = Loan(
        dataset_id=1,
        source_row_number=4,
        loan_id="LN-TEST-04",
        origination_date=date(2024, 1, 1),
        maturity_date=date(2020, 1, 1),  # before origination
        interest_rate=Decimal("85.0"),     # > 50%
        document_status="Complete",
    )
    exceptions = validate_loan(db, loan)
    codes = [e.rule_code for e in exceptions]
    assert "MATURITY_BEFORE_ORIGINATION" in codes
    assert "RATE_OUT_OF_RANGE" in codes


def test_validate_indian_state_code(db):
    """Invalid Indian state code should trigger INVALID_STATE_CODE."""
    loan_invalid = Loan(
        dataset_id=1,
        source_row_number=5,
        loan_id="LN-TEST-05",
        original_principal=Decimal("100000.00"),
        current_balance=Decimal("90000.00"),
        borrower_state="XX",  # Invalid
        document_status="Complete",
    )
    exceptions = validate_loan(db, loan_invalid)
    codes = [e.rule_code for e in exceptions]
    assert "INVALID_STATE_CODE" in codes

    loan_valid = Loan(
        dataset_id=1,
        source_row_number=6,
        loan_id="LN-TEST-06",
        original_principal=Decimal("100000.00"),
        current_balance=Decimal("90000.00"),
        borrower_state="DL",  # Valid Delhi
        document_status="Complete",
    )
    exceptions = validate_loan(db, loan_valid)
    codes = [e.rule_code for e in exceptions]
    assert "INVALID_STATE_CODE" not in codes


def test_validate_dataset_auto_verification(db, operator_token):
    """Validate dataset auto-verifies clean loans and records exceptions for broken loans."""
    token, user = operator_token

    dataset = Dataset(
        file_name="test_validation.csv",
        source_type=SourceType.LOAN_TAPE,
        uploaded_by=user.id,
        status=DatasetStatus.COMPLETED,
        total_rows=2,
        successfully_imported_rows=2,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # Loan 1: Clean
    loan1 = Loan(
        dataset_id=dataset.id,
        source_row_number=1,
        loan_id="LN-AUTO-01",
        borrower_id="BR-100",
        original_principal=Decimal("200000.00"),
        current_balance=Decimal("190000.00"),
        interest_rate=Decimal("5.0"),
        term_months=360,
        origination_date=date(2023, 1, 1),
        maturity_date=date(2053, 1, 1),
        borrower_state="DL",
        payment_status="Current",
        days_past_due=0,
        document_status="Complete",
    )
    # Loan 2: Invalid
    loan2 = Loan(
        dataset_id=dataset.id,
        source_row_number=2,
        loan_id="LN-AUTO-02",
        original_principal=Decimal("50000.00"),
        current_balance=Decimal("60000.00"),  # Exceeds principal
        document_status="Complete",
    )
    db.add_all([loan1, loan2])
    db.commit()

    result = validate_dataset(db, dataset.id, actor_id=user.id, actor_role=user.role.value)

    assert result["exceptions_created"] >= 1
    assert result["loans_auto_verified"] == 1

    db.refresh(loan1)
    db.refresh(loan2)
    assert loan1.verification_status == VerificationStatus.VERIFIED
    assert loan1.record_hash is not None
    assert loan2.verification_status == VerificationStatus.PENDING
