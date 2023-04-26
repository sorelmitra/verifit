from datetime import datetime

from verifit.config import get_store_reader
from verifit.date_diff import date_diff_in_minutes
from verifit.login import USER, DRIVER, get_expiry_date, login

from tests.shopping_service.login.shopping_service_login import shopping_login, shopping_get_main_user

get_env = get_store_reader()


def test_login_main_user():
    login_data = login({
        USER: shopping_get_main_user(),
        DRIVER: shopping_login,
    })
    minutes = date_diff_in_minutes(get_expiry_date(login_data))(datetime.now())
    assert 58 < minutes < 61
