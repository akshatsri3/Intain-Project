from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.security import verify_password, create_access_token


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
