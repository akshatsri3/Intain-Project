"""
Pytest configuration — sets up an in-memory SQLite test database
so tests don't require a running PostgreSQL instance.

The FastAPI lifespan calls Base.metadata.create_all(engine) using the
production PostgreSQL engine. We patch the engine in app.main to use
the test SQLite engine so the lifespan works without a real database.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.connection import get_db
from app.main import app as fastapi_app
import app.models  # noqa: F401

SQLITE_URL = "sqlite:///./test.db"

test_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    fastapi_app.dependency_overrides[get_db] = override_get_db

    # Patch the production engine in app.main so the lifespan
    # calls create_all on the SQLite test engine instead of PostgreSQL
    with patch("app.main.engine", test_engine):
        with TestClient(fastapi_app) as c:
            yield c

    fastapi_app.dependency_overrides.clear()


@pytest.fixture()
def operator_token(client, db):
    """Create a test operator user and return its JWT token."""
    from app.models.user import User, UserRole
    from app.utils.security import hash_password, create_access_token

    user = User(
        name="Test Operator",
        email="testop@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.DATA_OPERATOR,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return token, user
