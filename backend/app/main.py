import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Environment ──────────────────────────────────────────────────────────────
FRONTEND_URL = os.getenv("FRONTEND_URL", "")

# ── Database & models import (kept at module level so Vercel cold-starts fast) ──
from app.database.connection import engine
from app.database.base import Base

# Import all models so SQLAlchemy can register their tables.
# MUST happen before create_all().
import app.models  # noqa: F401

# ── Routers ──────────────────────────────────────────────────────────────────
from app.api import health, auth, datasets
from app.api import validation, reviews, verified, audit, loans


# ── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once per cold-start.
    Wrapped in try/except so a DB hiccup never prevents the API from starting.
    """
    # Create tables if they don't exist yet (idempotent on PostgreSQL)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured.")
    except Exception as exc:
        # Log the error but do NOT crash — the server should still start
        logger.warning("Database table creation warning (non-fatal): %s", exc)

    # Seed demo users on fresh databases (idempotent — skips existing users)
    try:
        from app.seed import seed
        seed()
    except Exception as exc:
        logger.warning("Demo user seeding warning (non-fatal): %s", exc)

    yield  # ← API is live from here until shutdown


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Loan Data Verification Copilot API",
    description="Full pipeline: ingestion, normalization, validation, AI review, verified records, audit trail",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Build origin list — always include local dev, add production URL if set.
origins = ["http://localhost:5173", "http://localhost:3000"]
if FRONTEND_URL:
    origins.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Root endpoint (no auth, no DB — confirms server is up) ────────────────────
@app.get("/", tags=["root"])
def root():
    return {"message": "Loan Data Verification Copilot API is running", "version": "2.0.0"}


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(validation.router)
app.include_router(reviews.router)
app.include_router(verified.router)
app.include_router(audit.router)
app.include_router(loans.router)
