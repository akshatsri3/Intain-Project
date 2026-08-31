import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database.connection import engine
from app.database.base import Base

# Import all models so SQLAlchemy can create their tables
import app.models  # noqa: F401

from app.api import health, auth, datasets
from app.api import validation, reviews, verified, audit, loans

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Loan Data Verification Copilot API",
    description="Full pipeline: ingestion, normalization, validation, AI review, verified records, audit trail",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow the React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(validation.router)
app.include_router(reviews.router)
app.include_router(verified.router)
app.include_router(audit.router)
app.include_router(loans.router)

