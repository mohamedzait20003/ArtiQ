from pydantic import BaseModel
from typing import Optional


class CreateUserRequest(BaseModel):
    """Request model for creating a new user"""
    name: str
    email: str
    password: str
    role_id: Optional[str] = None
    is_admin: bool = False


class UserResponse(BaseModel):
    """Response model for user data"""
    id: str
    name: str
    email: str
    role_id: Optional[str] = None
