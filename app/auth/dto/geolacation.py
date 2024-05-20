import typing
from piccolo_api.crud.serializers import create_pydantic_model

from auth.tables import UserGeolocation

GeolocationIn: typing.Any = create_pydantic_model(table=UserGeolocation, model_name="GeolocationIn")
GeolocationOut: typing.Any = create_pydantic_model(
    table=UserGeolocation, include_default_columns=True, model_name="GeolocationOut")
