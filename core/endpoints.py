from fastapi import APIRouter, HTTPException

# from app import router
from .tables import User, UserGeolocation
from .dto.auth import (
    LoginRequest, VerificationRequest, TokenResponse
)
from .dto.user import GeolocationIn, GeolocationOut
from .utils import send_verification_code, check_phone


class AuthEndpoint(APIRouter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tags = ['User Authentication']
        self.add_api_route(
            "/login",
            endpoint=self.login,
            methods=["POST"],
            response_model=TokenResponse
        )
        self.add_api_route(
            "/login/{token:str}/verify",
            endpoint=self.verify,
            methods=["POST"],
            response_model=TokenResponse
        )
        self.add_api_route(
            "/login/refresh",
            endpoint=self.token_refresh,
            methods=["POST"],
            response_model=TokenResponse
        )
        self.add_api_route(
            "/logout",
            endpoint=self.logout,
            methods=["POST"]
        )

    async def login(self, request: LoginRequest):
        phone_number = request.phone_number

        # phone number validation
        if not await check_phone(phone_number):
            raise HTTPException(status_code=400, detail="Invalid phone number")

        # send verification code
        user = User(username=phone_number, phone_number=phone_number)
        code = await user.create_verify_code()
        await user.save()
        await send_verification_code(code, phone_number)

    async def verify(self, token: str, request: VerificationRequest):
        ...

    async def token_refresh(self):
        ...

    async def logout(self):
        ...


class UserGeolocationEndpoint(APIRouter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tags = ['User Geolocation']
        self.add_api_route(
            "/{telegram_id}/geolocation",
            endpoint=self.create,
            response_model=GeolocationOut,
            methods=["POST"],
            tags=["User Geolocation"]
        )

    async def create(
            self,
            request: GeolocationIn
    ):
        geolocation = UserGeolocation(**request.dict())
        await geolocation.save()
        data = geolocation.to_dict()
        # await router.broker.publish(
        #     data,
        #     "main-topic",
        #     key="geolocation_created",
        # )
        return data


auth_router = AuthEndpoint()
geolocation_router = UserGeolocationEndpoint()
