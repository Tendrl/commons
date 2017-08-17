import datetime

from tendrl.commons.utils import time_utils


def test_now():
    date = time_utils.now()
    assert isinstance(date, datetime.datetime)
