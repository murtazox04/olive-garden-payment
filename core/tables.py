from piccolo.table import Table
from piccolo.apps.user.tables import BaseUser
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.columns import Varchar, BigInt, Float, Text, Timestamp, ForeignKey


class User(BaseUser, tablename='piccolo_user'):
    """
    User table.
    """

    email = Varchar(unique=True, null=True)
    phone_number = Varchar(length=20, unique=True)
    telegram_id = BigInt(unique=True)
    date_joined = Timestamp(default=TimestampNow(), null=True)


class UserGeolocation(Table):
    """
    User geolocation table.
    """

    user = ForeignKey(references=User)
    lat = Float()
    lng = Float()
    reference_point = Text()
