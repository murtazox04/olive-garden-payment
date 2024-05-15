import typing
from fastapi import APIRouter, HTTPException, status
from piccolo_api.crud.serializers import create_pydantic_model

from app import router
from .tables import User, UserGeolocation


UserCreateIn: typing.Any = create_pydantic_model(table=User, model_name="UserCreateIn")
UserCreatedOut: typing.Any = create_pydantic_model(
    table=User, include_default_columns=True, model_name="UserCreateOut")
GeolocationIn: typing.Any = create_pydantic_model(table=UserGeolocation, model_name="GeolocationIn")
GeolocationOut: typing.Any = create_pydantic_model(
    table=UserGeolocation, include_default_columns=True, model_name="GeolocationOut")


class AuthEndpoint(APIRouter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tags = ['User Authentication']
        self.add_api_route(
            "login",
            endpoint=self.login_user,
            methods=["POST"]
        )
        self.add_api_route(
            "/user/{telegram_id}/geolocation",
            endpoint=self.create_geolocation,
            response_model=GeolocationOut,
            methods=["POST"],
            tags=["User Geolocation"]
        )

    async def create_geolocation(self, payload: GeolocationIn):
        geolocation = UserGeolocation(**payload.dict())
        await geolocation.save()
        return geolocation.to_dict()

    async def login_user(self, phone_number: str):
        user = await User.objects().get(User.phone_number == phone_number)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

