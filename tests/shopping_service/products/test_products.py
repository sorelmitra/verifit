from verifit.login import DRIVER, USER, login_from_cache
from verifit.config import get_store_reader
from verifit.retrieve import LOG_PREFIX, AUTHORIZE, retrieve_http

from tests.shopping_service.login.shopping_service_login import shopping_get_main_user, shopping_login

get_env = get_store_reader()


def test_products():
    login_from_cache({USER: shopping_get_main_user(), DRIVER: shopping_login})
    url = f"{get_env('SHOPPING_SERVICE_URL')}/products/{1}"
    data = retrieve_http(url)({
        LOG_PREFIX: 'Get products',
        AUTHORIZE: True,
    })
    assert data.get('id', None) == 1
    assert len(data.get('title', '')) > 0
