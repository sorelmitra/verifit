from datetime import datetime

from verifit.config import get_env_reader
from verifit.date_tools import date_subtract_in_minutes
from verifit.login import get_expiry_date, login

from tests.shopping_service.login.shopping_service_login import shopping_login, shopping_get_main_user

get_env = get_env_reader()


def test_login_main_user():
    login_data = login(driver=shopping_login, **shopping_get_main_user())
    minutes = date_subtract_in_minutes(from_date=get_expiry_date(login_data), date_to_subtract=datetime.now())
    assert 58 < minutes < 61
