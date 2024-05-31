import jwt
from typing import Optional, Tuple
from datetime import datetime, timedelta
from fastapi import HTTPException

from core.tables import TokenStorage


class JWTTokenService:
    SECRET_KEY = "18wu_=5e9nw#1optw9=e%fng5%tuce3tz(39^5)0@*qt4_tu_p"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token expiration time for access token
    REFRESH_TOKEN_EXPIRE_DAYS = 30  # Token expiration time for refresh token
    PHONE_VERIFICATION_TOKEN_EXPIRE_MINUTES = 10  # Token expiration time for phone verification token

    @classmethod
    async def create_access_token(cls, user_id: int) -> str:
        expire_time = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        data_to_encode = {"user_id": user_id, "exp": expire_time}
        access_token = jwt.encode(data_to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        await TokenStorage.update({TokenStorage.access_token: access_token}).where(TokenStorage.user == user_id).run()
        return access_token

    @classmethod
    async def create_refresh_token(cls, user_id: int) -> Tuple[str, str]:
        refresh_expire_time = datetime.utcnow() + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
        access_expire_time = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)

        refresh_data = {"user_id": user_id, "exp": refresh_expire_time}
        access_data = {"user_id": user_id, "exp": access_expire_time}

        refresh_token = jwt.encode(refresh_data, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        access_token = jwt.encode(access_data, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

        await TokenStorage(user=user_id, access_token=access_token, refresh_token=refresh_token).save()
        return refresh_token, access_token

    @classmethod
    async def decode_access_token(cls, token: str) -> dict:
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @classmethod
    async def refresh_access_token(cls, refresh_token: str) -> Optional[Tuple[str, str]]:
        try:
            decoded_token = await cls.decode_access_token(refresh_token)
            if decoded_token:
                user_id = decoded_token["user_id"]
                new_access_token = await cls.create_access_token(user_id)
                return refresh_token, new_access_token
        except HTTPException:
            return None

    @classmethod
    async def create_phone_verification_token(cls, user_id: int) -> str:
        expire_time = datetime.utcnow() + timedelta(minutes=cls.PHONE_VERIFICATION_TOKEN_EXPIRE_MINUTES)
        data_to_encode = {"user_id": user_id, "exp": expire_time}
        return jwt.encode(data_to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
