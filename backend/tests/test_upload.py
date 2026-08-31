import io
from app.models.user import User, UserRole
from app.utils.security import hash_password, create_access_token


SAMPLE_CSV = b"""Loan ID,Borrower ID,Loan Type,Origination Date,Original Principal,Interest Rate,Term,State,Payment Status
LN-1001,BR-001,Mortgage,2024-01-15,$250000,6.5%,360,CA,Current
LN-1002,BR-002,Auto,01/20/2024,"$45,000",7.25%,60,TX,Current
LN-1003,BR-003,Personal,15-Mar-2024,$12000,0.115,36,NY,30-59 Days Past Due
"""

MALFORMED_CSV = b""",,,
,,,
"""


def _create_operator(db):
    user = User(
        name="Upload Operator",
        email="upload_op@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.DATA_OPERATOR,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_reviewer(db):
    user = User(
        name="Upload Reviewer",
        email="upload_rev@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.REVIEWER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_upload_as_operator(client, db):
    op = _create_operator(db)
    token = create_access_token({"sub": str(op.id), "role": op.role.value})

    response = client.post(
        "/datasets/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("loans.csv", io.BytesIO(SAMPLE_CSV), "text/csv")},
        data={"source_type": "LOAN_TAPE"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["dataset"]["file_name"] == "loans.csv"
    assert data["dataset"]["total_rows"] == 3
    assert data["dataset"]["successfully_imported_rows"] == 3
    assert data["dataset"]["status"] == "COMPLETED"
    assert data["normalization_summary"]["interest_rates_normalized"] == 3


def test_upload_as_reviewer_forbidden(client, db):
    rev = _create_reviewer(db)
    token = create_access_token({"sub": str(rev.id), "role": rev.role.value})

    response = client.post(
        "/datasets/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("loans.csv", io.BytesIO(SAMPLE_CSV), "text/csv")},
        data={"source_type": "LOAN_TAPE"},
    )
    assert response.status_code == 403


def test_upload_non_csv_rejected(client, db):
    op = _create_operator(db)
    token = create_access_token({"sub": str(op.id), "role": op.role.value})

    response = client.post(
        "/datasets/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("loans.xlsx", io.BytesIO(b"fake excel"), "application/octet-stream")},
        data={"source_type": "LOAN_TAPE"},
    )
    assert response.status_code == 400


def test_list_datasets(client, db):
    op = _create_operator(db)
    token = create_access_token({"sub": str(op.id), "role": op.role.value})

    response = client.get("/datasets", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
