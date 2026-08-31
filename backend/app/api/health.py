from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.connection import get_db

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check():
    """Basic health check — no DB required. Confirms the server process is running."""
    return {
        "status": "healthy",
        "service": "Loan Data Verification Copilot API",
    }


@router.get("/health/db", tags=["health"])
def health_db(db: Session = Depends(get_db)):
    """
    Database connectivity check.
    Returns 200 if the DB is reachable and the users table exists.
    Returns 500 if DB is unreachable — useful for diagnosing production issues.
    """
    try:
        # Run a trivial query to confirm DB is up and users table exists
        result = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        return {
            "status": "healthy",
            "database": "connected",
            "user_count": result,
        }
    except Exception as exc:
        # Return 500 with the actual DB error so we can diagnose it
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(exc)}",
        )
