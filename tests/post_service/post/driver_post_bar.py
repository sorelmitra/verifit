import requests
from verifit.config import get_store_reader
from verifit.retrieve import AUTHORIZE, LOG_PREFIX, METHOD, PAYLOAD, retrieveHttp

get_env = get_store_reader()


def driver_post_bar(post_id):
    url = f"{get_env('POST_SERVICE_1_URL')}/posts"
    payload = {
      "userId": post_id,
      "title": "test post",
      "body": "test post body"
    }
    data = retrieveHttp(url)({
        METHOD: requests.post,
        LOG_PREFIX: 'Post via Post-Service-1',
        PAYLOAD: payload,
        AUTHORIZE: True,
    })
    assert data is not None
    return {
        "id": data.get('userId', None),
        "title": data.get('title', None),
        "body": data.get('body', None),
    }
