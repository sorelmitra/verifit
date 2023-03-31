from verifit.config import get_store_reader
from verifit.retrieve import LOG_PREFIX, retrieveHttp


get_env = get_store_reader()

def driver_get_carts_foo(cart_id):
    url = f"{get_env('SHOPPING_SERVICE_URL')}/products/{cart_id}"
    data = retrieveHttp(url)({
        LOG_PREFIX: f"Get cart product {cart_id}",
    })
    assert data is not None
    return data
