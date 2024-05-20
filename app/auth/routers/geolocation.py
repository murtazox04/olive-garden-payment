from fastapi import APIRouter

# from app import router
from auth.tables import UserGeolocation
from auth.dto import GeolocationIn, GeolocationOut


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


geolocation_router = UserGeolocationEndpoint()
