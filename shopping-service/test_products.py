import requests

from lib.config import get_store_reader
from lib.login import get_bearer_authorization_header_value

get_env = get_store_reader()


def test_products():
    url = f"{get_env('SHOPPING_SERVICE_URL')}/products/1"
    print('Getting product 1 from shopping server')
    response = requests.get(
        url=url,
        headers={
            'Content-Type': 'application/json',
            'Authorization': get_bearer_authorization_header_value()
        },
    )
    data = response.json()
    assert data is not None
    assert data.get('id', None) == 1
    assert len(data.get('title', '')) > 0