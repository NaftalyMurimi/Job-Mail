from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    # bcrypt only uses the first 72 bytes, so cap the length there
    password: str = Field(min_length=8, max_length=72)
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    # No password field here, so it can never leak in a response
    id: str
    email: EmailStr
    full_name: str | None = None