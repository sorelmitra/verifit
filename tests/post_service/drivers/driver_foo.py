import requests

from verifit.config import get_env_reader
from verifit.retrieve import retrieve_http

get_env = get_env_reader()


def foo_post(*, userId, title, body):
    payload = {
        "userId": userId,
        "title": title,
        "body": body
    }
    url = f"{get_env('POST_SERVICE_1_URL')}/posts"
    return retrieve_http(url=url, method=requests.post,log_prefix='REST API Post', payload=payload)


def foo_check_post_response(*, response, userId):
    assert response is not None
    assert response.get('userId') == userId
    assert len(response.get('title', '')) > 0
    assert len(response.get('body', '')) > 0
