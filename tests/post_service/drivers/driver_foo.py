import requests

from verifit.config import get_store_reader
from verifit.retrieve import LOG_PREFIX, retrieve_http, METHOD, PAYLOAD

get_env = get_store_reader()


def foo_post(payload):
    url = f"{get_env('POST_SERVICE_1_URL')}/posts"
    return retrieve_http(url)({
        METHOD: requests.post,
        LOG_PREFIX: 'REST API Post',
        PAYLOAD: payload,
    })
