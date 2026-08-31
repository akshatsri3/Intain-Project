"""
Tests for Audit Trail API.
"""

from decimal import Decimal
from app.models.user import User, UserRole
from app.models.loan import Loan
from app.models.dataset import Dataset, SourceType, DatasetStatus
from app.services.audit_service import log_event
from app.utils.security import hash_password, create_access_token


def test_audit_trail_logging_and_querying(client, db):
    """Audit events logged during lifecycle can be retrieved via /audit endpoints."""
    operator = User(
        name="Operator Alice",
        email="audit_op@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.DATA_OPERATOR,
    )
    db.add(operator)
    db.commit()
    db.refresh(operator)
    token = create_access_token({"sub": str(operator.id), "role": operator.role.value})

    dataset = Dataset(
        file_name="audit_test.csv",
        source_type=SourceType.LOAN_TAPE,
        uploaded_by=operator.id,
        status=DatasetStatus.COMPLETED,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    loan = Loan(
        dataset_id=dataset.id,
        source_row_number=1,
        loan_id="LN-AUDIT-01",
        original_principal=Decimal("150000.00"),
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)

    # Log several events
    log_event(db, "loan", loan.id, "IMPORTED", actor_id=operator.id, actor_role="DATA_OPERATOR",
              details={"file": "audit_test.csv"})
    log_event(db, "loan", loan.id, "VALIDATION_RUN", actor_id=operator.id, actor_role="DATA_OPERATOR")
    log_event(db, "loan", loan.id, "VERIFIED_RECORD_CREATED", details={"method": "auto_verified"})
    db.commit()

    # Query loan audit trail
    resp = client.get(f"/audit/loan/{loan.id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    trail = resp.json()
    assert len(trail) == 3
    event_types = [e["event_type"] for e in trail]
    assert "IMPORTED" in event_types
    assert "VALIDATION_RUN" in event_types
    assert "VERIFIED_RECORD_CREATED" in event_types

    # Query recent events
    resp_recent = client.get("/audit/recent?entity_type=loan", headers={"Authorization": f"Bearer {token}"})
    assert resp_recent.status_code == 200
    recent = resp_recent.json()
    assert len(recent) >= 3
