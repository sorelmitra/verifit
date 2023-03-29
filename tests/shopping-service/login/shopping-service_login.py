import json

import requests

from verifit.config import get_store_reader
from verifit.login import PASSWORD, USERNAME
from verifit.prop import get_prop
from verifit.retrieve import LOG_PREFIX, METHOD, PAYLOAD, retrieveHttp

get_env = get_store_reader()


def execute(user):
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
