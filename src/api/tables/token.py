from datetime import timedelta, datetime
from piccolo.table import Table
from piccolo.columns import Varchar, BigInt, Timestamp


class TokenStorage(Table):
    """
    Model to store JWT tokens.
    """

    user_id = BigInt(unique=True)
    access_token = Varchar()
    refresh_token = Varchar()
    expiration_time = Timestamp(default=datetime.now() + timedelta(minutes=60))
