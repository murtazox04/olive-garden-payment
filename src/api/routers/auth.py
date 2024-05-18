from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException

from .utils import send_verification_code
from src.api.services import JWTTokenService
from src.api.tables import User, TokenStorage, UserConfirmation
from src.api.dto import LoginRequest, TokenResponse, VerificationRequest

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.add_api_route("/auth/login", self.login, methods=["POST"])
        self.add_api_route("/auth/login/{phone_verification_token}/verify", self.verify_phone_number, methods=["POST"])
        self.add_api_route("/auth/login/{refresh_token}/retry-verify", self.resend_verification_code, methods=["POST"])
        # self.add_api_route("/auth/logout", self.logout, methods=["POST"])

    async def login(self, request: LoginRequest):
        user = await User.objects().get_or_create(
            User.phone_number == request.phone_number,
            defaults={
                User.username: request.phone_number,
                User.password: request.telegram_id
            }
        )

        confirmation_code = await user.create_verify_code()
        # await user.save()
        print(confirmation_code)
        # await send_verification_code(confirmation_code, request.phone_number)

        phone_verification_token = JWTTokenService.create_phone_verification_token(user.id)

        return {"phone_verification_token": phone_verification_token}

    async def verify_phone_number(self, request: VerificationRequest):
        user_id = await self.get_current_user(request.phone_verification_token)
        user = await User.objects().get(User.id == user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        confirmation = await UserConfirmation.objects().where(
            UserConfirmation.user == user,
            UserConfirmation.code == request.verification_code,
            UserConfirmation.is_confirmed is False
        )
        if not confirmation[-1] or confirmation[-1].is_expired:
            raise HTTPException(status_code=401, detail="Invalid or expired verification code")

        confirmation.is_confirmed = True
        await confirmation[-1].save()

        access_token = JWTTokenService.create_access_token(user.id)
        refresh_token = JWTTokenService.create_refresh_token(user.id)

        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    async def resend_verification_code(self, request: VerificationRequest):
        user_id = await self.get_current_user(request.phone_verification_token)
        phone_verification_token = JWTTokenService.create_phone_verification_token(user_id)
        return {"phone_verification_token": phone_verification_token}

    # async def logout(self, token: str = Depends(oauth2_scheme)):
    #     user_id = await self.get_current_user(token)
    #     if user_id:
    #         token = await TokenStorage.objects().where(TokenStorage.user_id == user_id).first()
    #         await token.remove()
    #     return {"message": "Logged out successfully"}

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> int:
        payload = JWTTokenService.decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid access token")
        user_id = payload.get("user_id")
        return user_id


auth_router = AuthRouter()
