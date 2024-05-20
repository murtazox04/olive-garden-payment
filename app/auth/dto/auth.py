from pydantic import BaseModel


class LoginRequest(BaseModel):
    phone_number: str
    telegram_id: int


class VerificationRequest(BaseModel):
    code: str


class PhoneVerificationResponse(BaseModel):
    phone_verification_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
