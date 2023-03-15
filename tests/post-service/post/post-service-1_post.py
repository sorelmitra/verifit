import json

import requests

from verifit.config import get_store_reader

get_env = get_store_reader()


def execute(post_id):
    url = f"{get_env('POST_SERVICE_1_URL')}/posts"
    payload = {
      "userId": post_id,
      "title": "test post",
      "body": "test post body"
    }
    print(f"Posting via Post-Service-1 to {url}", payload)
    response = requests.post(
        url=url,
        data=json.dumps(payload),
        headers={
            'Content-Type': 'application/json'
        },
    )
    print('Received REST post response', response)
    data = response.json()
    print('Received REST post JSON response', data)
    assert data is not None
    return {
        "id": data.get('userId', None),
        "title": data.get('title', None),
        "body": data.get('body', None),
    }
