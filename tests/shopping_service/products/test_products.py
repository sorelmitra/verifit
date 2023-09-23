from verifit.login import login_from_cache
from verifit.config import get_store_reader
from verifit.retrieve import retrieve_http

from tests.shopping_service.login.shopping_service_login import shopping_get_main_user, shopping_login

get_env = get_store_reader()


def test_products():
    login_from_cache(driver=shopping_login, **shopping_get_main_user())
    url = f"{get_env('SHOPPING_SERVICE_URL')}/products/{1}"
    data = retrieve_http(url=url, log_prefix='Get products', use_auth=True)
    assert data.get('id', None) == 1
    assert len(data.get('title', '')) > 0
