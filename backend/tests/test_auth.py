from app.models.user import User, UserRole
from app.utils.security import hash_password


def _create_user(db, email, role):
    user = User(
        name="Test User",
        email=email,
        password_hash=hash_password("password123"),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_login_success(client, db):
    _create_user(db, "login_op@test.com", UserRole.DATA_OPERATOR)
    response = client.post("/auth/login", json={"email": "login_op@test.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, db):
    _create_user(db, "wrong_pw@test.com", UserRole.REVIEWER)
    response = client.post("/auth/login", json={"email": "wrong_pw@test.com", "password": "badpassword"})
    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post("/auth/login", json={"email": "nobody@test.com", "password": "password123"})
    assert response.status_code == 401


def test_get_me(client, db):
    _create_user(db, "me_op@test.com", UserRole.DATA_OPERATOR)
    login_resp = client.post("/auth/login", json={"email": "me_op@test.com", "password": "password123"})
    token = login_resp.json()["access_token"]

    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "me_op@test.com"
    assert me_resp.json()["role"] == "DATA_OPERATOR"


def test_get_me_no_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 403
