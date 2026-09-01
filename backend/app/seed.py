"""
Seed script — inserts three demo users into the database.

Called automatically from app lifespan on startup (idempotent).
Can also be run manually:
  cd backend
  python -m app.seed
"""

import sys
import os
import logging

logger = logging.getLogger(__name__)

# Allow running directly: python -m app.seed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal, engine
from app.database.base import Base
import app.models  # noqa: F401 — registers all ORM models
from app.models.user import User, UserRole
from app.utils.security import hash_password


def seed():
    """
    Create demo users if they don't already exist.
    Safe to call multiple times — never duplicates users.
    """
    # Ensure tables exist (no-op if already created)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        demo_users = [
            {
                "name": "Akshat Operator",
                "email": "operator@test.com",
                "password": "password123",
                "role": UserRole.DATA_OPERATOR,
            },
            {
                "name": "Akshat Reviewer",
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

        created = 0
        for user_data in demo_users:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                if existing.name != user_data["name"]:
                    existing.name = user_data["name"]
                    logger.info("  [UPDATE] %s -> %s", user_data["email"], user_data["name"])
                else:
                    logger.debug("  [SKIP] %s already exists", user_data["email"])
                continue

            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
            )
            db.add(user)
            created += 1
            logger.info("  [CREATE] %s (%s)", user_data["email"], user_data["role"].value)

        db.commit()
        if created:
            logger.info("Seeded %d demo user(s).", created)

    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Seeding database...")
    seed()
    print("Seed completed.")
