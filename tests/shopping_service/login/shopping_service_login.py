import requests

from verifit.config import get_env_reader
from verifit.retrieve import retrieve_http

get_env = get_env_reader()


def shopping_get_main_user():
    return {
        'username': get_env("SHOPPING_SERVICE_MAIN_USER_NAME"),
        'password': get_env("SHOPPING_SERVICE_MAIN_USER_PASSWORD"),
    }


def shopping_login(username=None, password=None):
    url = get_env('SHOPPING_SERVICE_LOGIN_ENDPOINT')
    data = retrieve_http(url=url, method=requests.post, log_prefix='Log in user',
                         payload={
                            'username': username,
                            'password': password,
                        })
    assert data is not None
    access_token = data.get('token', None)
    assert access_token is not None
    return access_token


