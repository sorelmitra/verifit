import json

import requests

from lib.config import get_store_reader, get_store_reader_low_case
from lib.login import get_login_user_name, get_login_user_password

get_env = get_store_reader()
get_env_low_case = get_store_reader_low_case()


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
    data = response.json()
    assert data is not None
    print(data)
    return {
        "id": data.get('userId', None),
        "title": data.get('title', None),
        "body": data.get('body', None),
    }
