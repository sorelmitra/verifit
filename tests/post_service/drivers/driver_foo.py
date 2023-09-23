import requests

from verifit.config import get_store_reader
from verifit.retrieve import retrieve_http

get_env = get_store_reader()


def foo_post(payload):
    url = f"{get_env('POST_SERVICE_1_URL')}/posts"
    return retrieve_http(url=url, method=requests.post,log_prefix='REST API Post', payload=payload)
