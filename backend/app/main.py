import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Configure logging so Vercel captures it
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Environment ──────────────────────────────────────────────────────────────
FRONTEND_URL = os.getenv("FRONTEND_URL", "").strip()

# ── Database & models import ──────────────────────────────────────────────────
from app.database.connection import engine
from app.database.base import Base

# Import all models so SQLAlchemy can register their tables (must be before create_all)
import app.models  # noqa: F401

# ── Routers ──────────────────────────────────────────────────────────────────
from app.api import health, auth, datasets
from app.api import validation, reviews, verified, audit, loans


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once per cold-start.
    Both create_all and seeding are wrapped in try/except so a DB issue
    never prevents the API from responding to health checks.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables ensured.")
    except Exception as exc:
        logger.error("❌ Database table creation FAILED: %s", exc)

    try:
        from app.seed import seed
        seed()
    except Exception as exc:
        logger.error("❌ Demo user seeding FAILED: %s", exc)

    # Log CORS config so it's visible in Vercel function logs
    logger.info("🔒 CORS allowed origins: %s", allowed_origins)

    yield


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Loan Data Verification Copilot API",
    description="Full pipeline: ingestion, normalization, validation, AI review, verified records, audit trail",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Build the allowed origins list.
# Always include local dev. Append the production frontend URL if configured.
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]
if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL)
    # Also add with and without trailing slash to be safe
    if FRONTEND_URL.endswith("/"):
        allowed_origins.append(FRONTEND_URL.rstrip("/"))
    else:
        allowed_origins.append(FRONTEND_URL + "/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Root (no auth, no DB) ─────────────────────────────────────────────────────
@app.get("/", tags=["root"])
def root():
    return {
        "message": "Loan Data Verification Copilot API is running",
        "version": "2.0.0",
    }


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(validation.router)
app.include_router(reviews.router)
app.include_router(verified.router)
app.include_router(audit.router)
app.include_router(loans.router)
