from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException, status, Path

from auth.services import JWTTokenService
from auth.tables import User, UserConfirmation, TokenStorage
from auth.dto import LoginRequest, VerificationRequest, PhoneVerificationResponse, TokenResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthRouter(APIRouter):
    def __init__(self):
        super().__init__()
        self.tags = ['Authentication']
        self.add_api_route("/login", self.login, methods=["POST"], response_model=PhoneVerificationResponse, status_code=status.HTTP_201_CREATED)
        self.add_api_route("/login/{phone_verification_token}/verify", self.verify_phone_number, methods=["POST"], response_model=TokenResponse)
        self.add_api_route("/login/{refresh_token}/retry-verify", self.resend_verification_code, methods=["POST"], response_model=PhoneVerificationResponse)
        self.add_api_route("/auth/logout", self.logout, methods=["POST"], response_model=dict, status_code=status.HTTP_200_OK)

    async def login(self, request: LoginRequest):
        user, created = await User.objects().get_or_create(
            User.phone_number == request.phone_number,
            defaults={
                User.username: request.phone_number,
                User.password: request.telegram_id
            }
        )
        if not created:
            user.password = request.telegram_id
            await user.save()

        confirmation_code = await user.create_verify_code()
        # await user.save()
        print(confirmation_code)
        # await send_verification_code(confirmation_code, request.phone_number)

        phone_verification_token = JWTTokenService.create_phone_verification_token(user.id)
        return {"phone_verification_token": phone_verification_token}

    async def verify_phone_number(self, request: VerificationRequest, phone_verification_token: str):
        user_id = await self.get_current_user(phone_verification_token)
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

    async def resend_verification_code(self, phone_verification_token: str):
        user_id = await self.get_current_user(phone_verification_token)
        verification_token = JWTTokenService.create_phone_verification_token(user_id)
        return {"phone_verification_token": verification_token}

    async def logout(self, token: str = Depends(oauth2_scheme)):
        user_id = await self.get_current_user(token)
        if user_id:
            token = await TokenStorage.objects().where(TokenStorage.user_id == user_id).first()
            if token:
                await token.remove()
        return {"message": "Logged out successfully"}

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> int:
        payload = JWTTokenService.decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid access token")
        user_id = payload.get("user_id")
        return user_id


auth_router = AuthRouter()
