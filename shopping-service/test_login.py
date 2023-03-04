from datetime import datetime

from lib.date_and_time import date_diff_in_minutes
from lib.login import login, get_expiry_date
from user import get_main_login_user


def test_login_main_user():
    user = get_main_login_user()
    login_data = login(user)
    minutes = date_diff_in_minutes(get_expiry_date(login_data), datetime.now())
    assert 58 < minutes < 61
