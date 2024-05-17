from app import router
from core.tables import User


@router.subscriber("auth-topic", group_id="user_created")
async def user_create(data: dict):
    await User(**data).save()


@router.subscriber("auth-topic", group_id='user_updated')
async def user_update(data: dict) -> None:
    await User.update({
        User.username: data['username'],
        User.first_name: data['first_name'],
        User.last_name: data['last_name'],
        User.email: data['email'],
        User.phone_number: data['phone_number'],
        User.telegram_id: data['telegram_id'],
        User.date_joined: data['date_joined'],
    }).where(User.id == data['id'])


@router.subscriber("auth-topic", group_id='user_deleted')
async def user_delete(data: dict) -> None:
    await User.delete().where(User.id == data['id'])
