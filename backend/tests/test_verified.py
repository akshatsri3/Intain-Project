"""
Tests for Verified Records, Export, and Portfolio Quality Score.
"""

from decimal import Decimal
from datetime import datetime, timezone
from app.models.user import User, UserRole
from app.models.loan import Loan, VerificationStatus
from app.models.dataset import Dataset, SourceType, DatasetStatus
from app.utils.security import hash_password, create_access_token


def test_list_verified_loans_and_stats(client, db):
    """Data consumer can fetch verified loans, quality score, and CSV export."""
    consumer = User(
        name="Consumer Carol",
        email="consumer_test@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.DATA_CONSUMER,
    )
    db.add(consumer)
    db.commit()
    db.refresh(consumer)
    token = create_access_token({"sub": str(consumer.id), "role": consumer.role.value})

    dataset = Dataset(
        file_name="verified_test.csv",
        source_type=SourceType.LOAN_TAPE,
        uploaded_by=consumer.id,
        status=DatasetStatus.COMPLETED,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # 1 Verified Loan, 1 Pending Loan
    loan_ver = Loan(
        dataset_id=dataset.id,
        source_row_number=1,
        loan_id="LN-GOLD-01",
        borrower_id="BR-500",
        loan_type="Mortgage",
        original_principal=Decimal("300000.00"),
        current_balance=Decimal("280000.00"),
        interest_rate=Decimal("6.0"),
        verification_status=VerificationStatus.VERIFIED,
        record_hash="abc123hash",
        verified_at=datetime.now(timezone.utc),
    )
    loan_pend = Loan(
        dataset_id=dataset.id,
        source_row_number=2,
        loan_id="LN-PEND-01",
        original_principal=Decimal("100000.00"),
        verification_status=VerificationStatus.PENDING,
    )
    db.add_all([loan_ver, loan_pend])
    db.commit()

    # Test GET /verified/loans
    resp = client.get("/verified/loans", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    loans = resp.json()
    assert len(loans) == 1
    assert loans[0]["loan_id"] == "LN-GOLD-01"
    assert loans[0]["record_hash"] == "abc123hash"

    # Test GET /verified/stats
    resp_stats = client.get("/verified/stats", headers={"Authorization": f"Bearer {token}"})
    assert resp_stats.status_code == 200
    stats = resp_stats.json()
    assert stats["verified"] == 1
    assert stats["pending"] == 1
    assert stats["quality_score"] == 50.0

    # Test GET /verified/export?format=csv
    resp_csv = client.get("/verified/export?format=csv", headers={"Authorization": f"Bearer {token}"})
    assert resp_csv.status_code == 200
    assert "LN-GOLD-01" in resp_csv.text

    # Test GET /verified/export?format=json
    resp_json = client.get("/verified/export?format=json", headers={"Authorization": f"Bearer {token}"})
    assert resp_json.status_code == 200
    json_data = resp_json.json()
    assert len(json_data) == 1
    assert json_data[0]["loan_id"] == "LN-GOLD-01"
