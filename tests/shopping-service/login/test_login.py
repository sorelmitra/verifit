from datetime import datetime

import pytest

from verifit.date_and_time import date_diff_in_minutes
from verifit.login import login_main_user, get_expiry_date


@pytest.mark.driver_functionality('login')
def test_login_main_user(shopping_driver):
    login_data = login_main_user(shopping_driver)
    minutes = date_diff_in_minutes(get_expiry_date(login_data), datetime.now())
    assert 58 < minutes < 61
