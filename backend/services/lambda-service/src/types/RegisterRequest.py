from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """Request model for user registration"""
    name: str
    email: EmailStr
    password: str
