from datetime import datetime

from verifit.date_and_time import date_diff, in_minutes
from verifit.driver import get_driver
from verifit.login import get_expiry_date, login, login_main_user


def test_login_main_user(shopping_driver_name):
    user = get_driver(shopping_driver_name)('user')('MAIN')
    login_data = login(user)(get_driver(shopping_driver_name)('login'))
    minutes = date_diff(get_expiry_date(login_data))(datetime.now())(in_minutes())()
    assert 58 < minutes < 61


def test_login_main_user_with_shortcut(shopping_driver_name):
    login_data = login_main_user(shopping_driver_name)
    minutes = date_diff(get_expiry_date(login_data))(datetime.now())(in_minutes())()
    assert 58 < minutes < 61
