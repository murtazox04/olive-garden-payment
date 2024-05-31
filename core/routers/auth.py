from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException, status

from core.services import JWTTokenService
from core.tables import UserAccount, UserConfirmation, TokenStorage
from core.dto import LoginRequest, VerificationRequest, PhoneVerificationResponse, TokenResponse, RefreshTokenRequest

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token_placeholder")


class AuthRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.tags = ['Authentication']
        self.add_api_route(
            "/login",
            self.login,
            methods=["POST"],
            response_model=PhoneVerificationResponse,
            status_code=status.HTTP_201_CREATED
        )
        self.add_api_route(
            "/login/{phone_verification_token}/verify",
            self.verify_phone_number,
            methods=["POST"],
            response_model=TokenResponse
        )
        self.add_api_route(
            "/login/{phone_verification_token}/retry-verify",
            self.resend_verification_code, methods=["POST"],
            response_model=PhoneVerificationResponse
        )
        self.add_api_route(
            "/refresh",
            self.refresh,
            methods=["POST"],
            response_model=TokenResponse
        )
        self.add_api_route(
            "/logout",
            self.logout,
            methods=["POST"],
            response_model=dict,
            status_code=status.HTTP_200_OK
        )

    async def login(self, request: LoginRequest):
        print(1)
        user = await UserAccount.objects().get_or_create(
            UserAccount.phone_number == request.phone_number
        )
        if user._was_created:
            user.password = str(request.telegram_id)
            await user.save()

        confirmation_code = await user.create_verify_code()
        # await user.save()
        print(confirmation_code)
        # await send_verification_code(confirmation_code, request.phone_number)

        phone_verification_token = await JWTTokenService.create_phone_verification_token(user.id)
        return {"phone_verification_token": phone_verification_token}

    async def verify_phone_number(self, request: VerificationRequest, phone_verification_token: str):
        user_id = await self.get_current_user(phone_verification_token)
        user = await UserAccount.objects().get(UserAccount.id == user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        confirmation = await UserConfirmation.objects().get(
            (UserConfirmation.user == user)
            & (UserConfirmation.code == request.code)
            & (UserConfirmation.is_confirmed == False)
        )
        if not confirmation or confirmation.is_expired():
            raise HTTPException(status_code=401, detail="Invalid or expired verification code")

        confirmation.is_confirmed = True
        await confirmation.save()

        refresh_token, access_token = await JWTTokenService.create_refresh_token(user.id)
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def resend_verification_code(self, phone_verification_token: str):
        user_id = await self.get_current_user(phone_verification_token)
        verification_token = await JWTTokenService.create_phone_verification_token(user_id)

        user = UserAccount.objects().get(UserAccount.id == user_id)
        confirmation_code = await user.create_verify_code()
        print(confirmation_code)

        return {"phone_verification_token": verification_token}

    async def refresh(self, request: RefreshTokenRequest):
        refresh_token, new_access_token = await JWTTokenService.refresh_access_token(request.refresh_token)
        if not new_access_token:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        return {"access_token": new_access_token, "refresh_token": refresh_token}

    async def logout(self, token: str = Depends(oauth2_scheme)):
        user_id = await self.get_current_user(token)
        if user_id:
            token = await TokenStorage.objects().where(TokenStorage.user == user_id).first()
            if token:
                await token.remove()
        return {"message": "Logged out successfully"}

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> int:
        payload = await JWTTokenService.decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid access token")
        user_id = payload.get("user_id")
        return user_id


auth_router = AuthRouter()
