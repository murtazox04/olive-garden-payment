import typing
from piccolo_api.crud.serializers import create_pydantic_model

from core.tables import User, UserGeolocation

UserCreateIn: typing.Any = create_pydantic_model(table=User, model_name="UserCreateIn")
UserCreatedOut: typing.Any = create_pydantic_model(
    table=User, include_default_columns=True, model_name="UserCreateOut")
GeolocationIn: typing.Any = create_pydantic_model(table=UserGeolocation, model_name="GeolocationIn")
GeolocationOut: typing.Any = create_pydantic_model(
    table=UserGeolocation, include_default_columns=True, model_name="GeolocationOut")
