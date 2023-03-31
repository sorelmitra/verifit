import requests

from verifit.config import get_store_reader
from verifit.login import PASSWORD, USERNAME
from verifit.prop import get_prop
from verifit.retrieve import LOG_PREFIX, METHOD, PAYLOAD, retrieveHttp

get_env = get_store_reader()


def get_main_user():
    user_type = 'MAIN'
    username = get_env(f"SHOPPING_SERVICE_{user_type}_USER_NAME")
    password = get_env(f"SHOPPING_SERVICE_{user_type}_USER_PASSWORD")
    return {
        USERNAME: username,
        PASSWORD: password,
    }


def login_before_test(user):
    url = get_env('SHOPPING_SERVICE_LOGIN_ENDPOINT')
    data = retrieveHttp(url)({
        METHOD: requests.post,
        LOG_PREFIX: 'Log in user',
        PAYLOAD: {
            'username': get_prop(user)(USERNAME),
            'password': get_prop(user)(PASSWORD),
        },
    })
    assert data is not None
    access_token = data.get('token', None)
    assert access_token is not None
    return access_token
