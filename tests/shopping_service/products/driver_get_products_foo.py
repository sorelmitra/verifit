from verifit.config import get_store_reader
from verifit.retrieve import AUTHORIZE, LOG_PREFIX, retrieve_http

get_env = get_store_reader()


def driver_get_products_foo(an_id):
    url = f"{get_env('SHOPPING_SERVICE_URL')}/products/{an_id}"
    data = retrieve_http(url)({
        LOG_PREFIX: 'Get products',
        AUTHORIZE: True,
    })
    assert data is not None
    return data

