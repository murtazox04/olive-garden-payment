from faststream.kafka.fastapi import KafkaRouter

from core.tables import User

router = KafkaRouter("localhost:9092")


@router.subscriber("auth-topic", key_deserializer=b'user_created')
async def user_created(data: dict) -> None:
    user = User(**data)
    await user.save()


@router.subscriber("auth-topic", key_deserializer=b'user_updated')
async def user_updated(data: dict) -> None:
    await User.update({
        User.username: data['username'],
        User.first_name: data['first_name'],
        User.last_name: data['last_name'],
        User.email: data['email'],
        User.phone_number: data['phone_number'],
        User.telegram_id: data['telegram_id'],
        User.date_joined: data['date_joined'],
    }).where(User.id == data['id'])


@router.subscriber("auth-topic", key_deserializer=b'user_deleted')
async def user_deleted(data: dict) -> None:
    await User.delete().where(User.id == data['id'])
