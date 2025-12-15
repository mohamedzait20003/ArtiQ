from pydantic import BaseModel


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
    role: str
    userData: dict


class RegisterRequest(BaseModel):
    """Request model for user registration"""
    name: str
    email: str
    password: str
    confirm_password: str


class RegisterResponse(BaseModel):
    """Response model for successful registration"""
    token: str
    role: str
    userData: dict
