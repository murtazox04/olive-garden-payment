from pydantic import BaseModel


class LoginRequest(BaseModel):
    phone_number: str
    telegram_id: int


class VerificationRequest(BaseModel):
    phone_verification_token: str
    verification_code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
