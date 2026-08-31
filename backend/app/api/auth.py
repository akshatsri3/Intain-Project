from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import authenticate_user, create_token_for_user, register_user
from app.utils.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - Validates email format (Pydantic EmailStr)
    - Validates role is one of: DATA_OPERATOR, REVIEWER, DATA_CONSUMER
    - Returns 400 if email already registered
    - Password is hashed — never stored or returned in plain text
    """
    # Password length check (minimum 8 characters)
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long.",
        )

    user = register_user(
        db=db,
        name=request.name.strip(),
        email=request.email,
        password=request.password,
        role=request.role,
    )
    return user  # UserResponse — no password_hash


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Sign in and receive a JWT access token",
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email + password and receive a JWT token.

    The response includes a `user` object so the frontend
    does not need a separate /auth/me call after login.
    """
    user = authenticate_user(db, request.email, request.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_token_for_user(user)
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return current_user
