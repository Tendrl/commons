import datetime
from pytz import utc


def now():
    """A tz-aware now

    """
    return datetime.datetime.utcnow().replace(tzinfo=utc)
