import pytest
import requests

from verifit.config import get_store_reader
from verifit.login import get_bearer_authorization_header_value, login_from_cache
from verifit.driver import get_functionality_per_driver

get_env = get_store_reader()


@pytest.mark.driver_functionality('login')
def test_products(shopping_driver):
    user = get_functionality_per_driver(shopping_driver)('get-main-login-user')()
    login_from_cache(user)(shopping_driver)
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
