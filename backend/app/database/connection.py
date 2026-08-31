import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    # Fallback to SQLite for local dev if no DATABASE_URL is set
    logger.warning(
        "DATABASE_URL not set — falling back to local SQLite (loan_copilot.db). "
        "Set DATABASE_URL in your .env file for PostgreSQL."
    )
    DATABASE_URL = "sqlite:///./loan_copilot.db"

# Heroku / Vercel Postgres / Railway may give a "postgres://" URL.
# SQLAlchemy requires "postgresql://" (or "postgresql+psycopg2://").
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency — provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
