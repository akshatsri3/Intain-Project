from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.utils.security import verify_password, hash_password, create_access_token


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Return the User if credentials are valid, else None."""
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_token_for_user(user: User) -> str:
    """Generate a JWT for the given user."""
    return create_access_token(data={"sub": str(user.id), "role": user.role.value})


def register_user(db: Session, name: str, email: str, password: str, role: UserRole) -> User:
    """
    Create a new user account.

    Raises:
        HTTPException 400 if the email is already registered.
    """
    # Check for duplicate email (case-insensitive)
    existing = db.query(User).filter(User.email == email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Hash password using the existing utility — never store plain text
    user = User(
        name=name,
        email=email.lower(),          # normalise to lowercase
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
