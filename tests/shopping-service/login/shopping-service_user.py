from verifit.config import get_store_reader
from verifit.login import create_login_user

get_env = get_store_reader()


def execute(user_type):
    username = get_env(f"SHOPPING_SERVICE_{user_type}_USER_NAME")
    password = get_env(f"SHOPPING_SERVICE_{user_type}_USER_PASSWORD")
    return create_login_user()(username)(password)
