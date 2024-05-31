import random
from datetime import datetime, timedelta
from piccolo.table import Table
from piccolo.apps.user.tables import BaseUser
from piccolo.columns import Varchar, BigInt, Boolean, Timestamp, ForeignKey, Float, Text


class UserConfirmation(Table):
    """
    User Confirmation table.
    """
    code = Varchar(length=6)
    user = ForeignKey(references="UserAccount")
    expiration_time = Timestamp(null=True)
    is_confirmed = Boolean()

    @classmethod
    async def mark_as_confirmed(cls, instance):
        """
        Marks the confirmation code as confirmed.
        """
        instance.is_confirmed = True
        await instance.save()

    def is_expired(self) -> bool:
        """
        Checks if the confirmation code has expired.
        """
        if self.expiration_time is not None:
            return datetime.now() > self.expiration_time
        return False


class UserAccount(BaseUser, tablename="user_account"):
    """
    User table.
    """
    email = Varchar(unique=True, null=True)
    phone_number = Varchar(length=20, unique=True)
    telegram_id = BigInt(unique=True)
    date_joined = Timestamp(default=datetime.now(), null=True)

    async def create_verify_code(self) -> str:
        code = "".join([str(random.randint(0, 9)) for _ in range(6)])  # Generate a 6-digit random code
        expiration = datetime.now() + timedelta(minutes=3)
        confirmation = UserConfirmation(user=self, code=code, expiration_time=expiration)
        await confirmation.save()
        return code


class TokenStorage(Table):
    """
    Model to store JWT tokens.
    """
    user = ForeignKey(references=UserAccount)
    access_token = Varchar()
    refresh_token = Varchar()


class UserGeolocation(Table):
    """
    User geolocation table.
    """
    user = ForeignKey(references="UserAccount")
    lat = Float()
    lng = Float()
    reference_point = Text()
    created_at = Timestamp(default=datetime.now(), null=True)
    updated_at = Timestamp(auto_update=datetime.now(), null=True)
