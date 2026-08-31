from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    """Request body for POST /auth/register."""
    name: str
    email: EmailStr          # validated email format
    password: str
    role: UserRole           # must be one of the existing UserRole enum values


class UserResponse(BaseModel):
    """Returned whenever we expose a user object — never includes password."""
    id: int
    name: str
    email: str
    role: UserRole

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Returned by /auth/login. user is optional so existing callers still work."""
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None
