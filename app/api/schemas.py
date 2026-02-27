from pydantic import BaseModel, EmailStr
from uuid import UUID


class RegisterSchema(BaseModel):
    email: EmailStr
    password: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshSchema(BaseModel):
    refresh_token: str