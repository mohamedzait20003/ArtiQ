from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    """User information for authentication"""
    name: str
    is_admin: bool = False


class Secret(BaseModel):
    """Secret credentials for authentication"""
    password: str


class AuthenticationRequest(BaseModel):
    """Request model for authentication"""
    user: User
    secret: Secret


class AuthenticationToken(BaseModel):
    """Response model for successful authentication"""
    value: str


class LoginRequest(BaseModel):
    """Request model for user login"""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Response model for successful login"""
    token: str


class RegisterRequest(BaseModel):
    """Request model for user registration"""
    email: str
    password: str
    name: Optional[str] = None
