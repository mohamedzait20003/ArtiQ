from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str
