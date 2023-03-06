from datetime import datetime

import pytest

from src.lib.date_and_time import date_diff_in_minutes
from src.lib.login import login, get_expiry_date
from user import get_main_login_user


@pytest.mark.driver_functionality('login')
def test_login_main_user(shopping_driver):
    user = get_main_login_user()
    login_data = login(user)(shopping_driver)
    minutes = date_diff_in_minutes(get_expiry_date(login_data), datetime.now())
    assert 58 < minutes < 61
