from pydantic import BaseModel


class LoginResponse(BaseModel):
    """Response model for successful login"""
    token: str
