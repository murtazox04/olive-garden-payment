import random
import typing as t
from datetime import datetime, timedelta
from piccolo.table import Table
from piccolo.query import Insert, Update
from piccolo.apps.user.tables import BaseUser
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.columns import Varchar, BigInt, Float, Boolean, Text, Timestamp, ForeignKey, Column


class UserConfirmation(Table):
    """
    User Confirmation table.
    """

    id: BigInt(primary_key=True)
    code = Varchar(length=6)
    user = ForeignKey("piccolo_user")
    expiration_time = Timestamp(null=True)
    is_confirmed = Boolean()

    def save(
            self, columns: t.Optional[t.Sequence[t.Union[Column, str]]] = None
    ) -> t.Union[Insert, Update]:
        if not self.id:
            self.expiration_time = datetime.now() + timedelta(minutes=3)
        return super(UserConfirmation, self).save(columns=columns)


class User(BaseUser, tablename="piccolo_user"):
    """
    User table.
    """

    email = Varchar(unique=True, null=True)
    phone_number = Varchar(length=20, unique=True)
    telegram_id = BigInt(unique=True)
    date_joined = Timestamp(default=TimestampNow(), null=True)

    async def create_verify_code(self) -> str:
        code = "".join([str(random.randint(0, 100) % 10) for _ in range(6)])
        confirmation = UserConfirmation(user=self, code=code)
        await confirmation.save()
        return code

    async def tokens(self) -> dict:
        ...