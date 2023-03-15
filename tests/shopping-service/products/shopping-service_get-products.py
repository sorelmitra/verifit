import requests

from verifit.config import get_store_reader
from verifit.login import get_bearer_authorization_header_value

get_env = get_store_reader()


def execute(an_id):
    url = f"{get_env('SHOPPING_SERVICE_URL')}/products/{an_id}"
    print('Getting product from shopping server', an_id)
    response = requests.get(
        url=url,
        headers={
            'Content-Type': 'application/json',
            'Authorization': get_bearer_authorization_header_value()
        },
    )
    print('Received product response', response)
    data = response.json()
    assert data is not None
    return data

