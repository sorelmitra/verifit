from verifit.config import get_store_reader
from verifit.login import create_login_user

get_env = get_store_reader()


def execute():
    username = get_env("SHOPPING_SERVICE_MAIN_USER_NAME")
    password = get_env("SHOPPING_SERVICE_MAIN_USER_PASSWORD")
    return create_login_user()(username)(password)
