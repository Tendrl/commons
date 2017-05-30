import pytest
from tendrl.commons.utils import time_utils
import datetime


def test_now():
    date = time_utils.now()
    assert type(date) == datetime.datetime


