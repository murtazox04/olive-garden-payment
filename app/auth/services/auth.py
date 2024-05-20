import jwt
from typing import Optional
from datetime import datetime, timedelta

from auth.tables import TokenStorage


class JWTTokenService:
    SECRET_KEY = "your_secret_key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token expiration time for access token
    REFRESH_TOKEN_EXPIRE_DAYS = 30  # Token expiration time for refresh token
    PHONE_VERIFICATION_TOKEN_EXPIRE_MINUTES = 10  # Token expiration time for phone verification token

    @classmethod
    async def create_access_token(cls, user_id: int) -> str:
        expire_time = datetime.now() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        data_to_encode = {"user_id": user_id, "exp": expire_time}
        access_token = jwt.encode(data_to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        TokenStorage(user_id=user_id, access_token=access_token).save().run_sync()
        return access_token

    @classmethod
    async def create_refresh_token(cls, user_id: int) -> str:
        expire_time = datetime.now() + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
        data_to_encode = {"user_id": user_id, "exp": expire_time}
        refresh_token = jwt.encode(data_to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        TokenStorage(user_id=user_id, refresh_token=refresh_token).save().run_sync()
        return refresh_token

    @classmethod
    async def decode_access_token(cls, token: str) -> dict:
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError

    @classmethod
    async def refresh_access_token(cls, refresh_token: str) -> Optional[str]:
        decoded_token = cls.decode_access_token(refresh_token)
        if decoded_token:
            user_id = decoded_token.get("user_id")
            new_access_token = await cls.create_access_token(user_id)
            return new_access_token
        return None

    @classmethod
    async def create_phone_verification_token(cls, user_id: int) -> str:
        expire_time = datetime.now() + timedelta(minutes=cls.PHONE_VERIFICATION_TOKEN_EXPIRE_MINUTES)
        data_to_encode = {"user_id": user_id, "exp": expire_time}
        return jwt.encode(data_to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
