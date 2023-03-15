import requests

from verifit.config import get_store_reader
from verifit.login import get_bearer_authorization_header_value

get_env = get_store_reader()


def execute(an_id):
    url = f"{get_env('SHOPPING_SERVICE_URL')}/products/{an_id}"
    print(f"Getting product from {url}", an_id)
    response = requests.get(
        url=url,
        headers={
            'Content-Type': 'application/json',
            'Authorization': get_bearer_authorization_header_value()
        },
    )
    print(f"Received product response from {url}", response)
    data = response.json()
    print(f"Received product JSON response from {url}", data)
    assert data is not None
    return data

