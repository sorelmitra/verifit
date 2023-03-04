from datetime import datetime

from lib.config import get_store_reader
from lib.date_and_time import date_diff_in_minutes
from lib.login import login, create_login_user, get_expiry_date

get_env = get_store_reader()


def get_main_login_user():
    username = get_env("SHOPPING_SERVICE_MAIN_USER_NAME")
    password = get_env("SHOPPING_SERVICE_MAIN_USER_PASSWORD")
    return create_login_user()(username)(password)


def test_login_main_user():
    user = get_main_login_user()
    login_data = login(user)
    minutes = date_diff_in_minutes(get_expiry_date(login_data), datetime.now())
    assert 58 < minutes < 61
