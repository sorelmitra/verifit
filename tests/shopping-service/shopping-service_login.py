import json

import requests

from verifit.config import get_store_reader
from verifit.login import get_login_user_name, get_login_user_password

get_env = get_store_reader()


def execute(user):
    url = get_env('SHOPPING_SERVICE_LOGIN_ENDPOINT')
    print('Logging in user in to shopping server', user)
    response = requests.post(
        url=url,
        data=json.dumps({
            'username': get_login_user_name(user),
            'password': get_login_user_password(user),
        }),
        headers={
            'Content-Type': 'application/json'
        },
    )
    data = response.json()
    assert data is not None
    access_token = data.get('token', None)
    assert access_token is not None
    return access_token
