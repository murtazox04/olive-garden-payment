from piccolo.table import Table
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.columns import Float, Text, Timestamp, ForeignKey

from .user import User


class UserGeolocation(Table):
    """
    User geolocation table.
    """

    user = ForeignKey(references=User)
    lat = Float()
    lng = Float()
    reference_point = Text()
    created_at = Timestamp(default=TimestampNow(), null=True)
    updated_at = Timestamp(auto_update=TimestampNow(), null=True)
