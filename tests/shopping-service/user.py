from src.lib.config import get_store_reader
from src.lib.login import create_login_user

get_env = get_store_reader()


def get_main_login_user():
    username = get_env("SHOPPING_SERVICE_MAIN_USER_NAME")
    password = get_env("SHOPPING_SERVICE_MAIN_USER_PASSWORD")
    return create_login_user()(username)(password)
