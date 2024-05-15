from pydantic import BaseModel


class LoginRequest(BaseModel):
    phone_number: str


class VerificationRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
