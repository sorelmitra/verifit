from datetime import datetime

from verifit.date_diff import date_diff_in_minutes
from verifit.login import DRIVER, USER, get_expiry_date, login

from driver_get_user_all import all_get_user_drivers
from driver_login_all import all_login_drivers


def test_login_main_user(select_current_shopping_driver):
    get_user_driver = select_current_shopping_driver(all_get_user_drivers())
    user = get_user_driver('MAIN')
    login_driver = select_current_shopping_driver(all_login_drivers())
    login_data = login({USER: user, DRIVER: login_driver})
    minutes = date_diff_in_minutes(get_expiry_date(login_data))(datetime.now())
    assert 58 < minutes < 61
