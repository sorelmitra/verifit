import requests

from verifit.config import get_store_reader
from verifit.login import PASSWORD, USERNAME
from verifit.retrieve import LOG_PREFIX, METHOD, PAYLOAD, retrieve_http

get_env = get_store_reader()


def shopping_get_main_user():
    return {
        USERNAME: get_env("SHOPPING_SERVICE_MAIN_USER_NAME"),
        PASSWORD: get_env("SHOPPING_SERVICE_MAIN_USER_PASSWORD"),
    }


def shopping_login(user):
    url = get_env('SHOPPING_SERVICE_LOGIN_ENDPOINT')
    data = retrieve_http(url)({
        METHOD: requests.post,
        LOG_PREFIX: 'Log in user',
        PAYLOAD: {
            'username': user[USERNAME],
            'password': user[PASSWORD],
        },
    })
    assert data is not None
    access_token = data.get('token', None)
    assert access_token is not None
    return access_token


