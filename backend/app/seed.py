"""
Seed script — inserts three test users into the database.

Run with:
  cd backend
  python -m app.seed
"""

import sys
import os

# Ensure the backend directory is on the path when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal, engine
from app.database.base import Base
import app.models  # noqa: F401 — ensures models are registered
from app.models.user import User, UserRole
from app.utils.security import hash_password


def seed():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        test_users = [
            {
                "name": "Alice Operator",
                "email": "operator@test.com",
                "password": "password123",
                "role": UserRole.DATA_OPERATOR,
            },
            {
                "name": "Bob Reviewer",
                "email": "reviewer@test.com",
                "password": "password123",
                "role": UserRole.REVIEWER,
            },
            {
                "name": "Carol Consumer",
                "email": "consumer@test.com",
                "password": "password123",
                "role": UserRole.DATA_CONSUMER,
            },
        ]

        for user_data in test_users:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f"  [SKIP] {user_data['email']} already exists")
                continue

            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
            )
            db.add(user)
            print(f"  [CREATE] {user_data['email']} ({user_data['role'].value})")

        db.commit()
        print("\nSeed completed successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding database...")
    seed()
