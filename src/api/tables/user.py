import random
from datetime import datetime, timedelta
from piccolo.table import Table
from piccolo.apps.user.tables import BaseUser
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.columns import Varchar, BigInt, Boolean, Timestamp, ForeignKey


class UserConfirmation(Table):
    """
    User Confirmation table.
    """

    code = Varchar(length=6)
    user = ForeignKey("piccolo_user")
    expiration_time = Timestamp(null=True, default=datetime.now() + timedelta(minutes=3))
    is_confirmed = Boolean()

    @classmethod
    async def mark_as_confirmed(cls, instance):
        """
        Marks the confirmation code as confirmed.
        """
        instance.is_confirmed = True
        await instance.save()

    @classmethod
    def is_expired(cls, instance) -> bool:
        """
        Checks if the confirmation code has expired.
        """
        if instance.expiration_time is not None:
            return datetime.now() > instance.expiration_time
        return False


class User(BaseUser, tablename="piccolo_user"):
    """
    User table.
    """

    email = Varchar(unique=True, null=True)
    phone_number = Varchar(length=20, unique=True)
    telegram_id = BigInt(unique=True)
    date_joined = Timestamp(default=TimestampNow(), null=True)

    async def create_verify_code(self) -> str:
        code = "".join([str(random.randint(0, 9)) for _ in range(6)])  # Generate a 6-digit random code
        confirmation = UserConfirmation(user=self, code=code)
        await confirmation.save()
        return code
