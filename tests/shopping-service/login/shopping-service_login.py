import json

import requests

from verifit.config import get_store_reader
from verifit.login import PASSWORD, USERNAME
from verifit.prop import get_prop

get_env = get_store_reader()


def execute(user):
    url = get_env('SHOPPING_SERVICE_LOGIN_ENDPOINT')
    print(f"Logging in user in to {url}", user)
    response = requests.post(
        url=url,
        data=json.dumps({
            'username': get_prop(user)(USERNAME),
            'password': get_prop(user)(PASSWORD),
        }),
        headers={
            'Content-Type': 'application/json'
        },
    )
    print(f"Received login response from {url}", response)
    data = response.json()
    print(f"Received login JSON response from {url}", data)
    assert data is not None
    access_token = data.get('token', None)
    assert access_token is not None
    return access_token
