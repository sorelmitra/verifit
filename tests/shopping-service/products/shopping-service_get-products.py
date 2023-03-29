from verifit.config import get_store_reader
from verifit.retrieve import LOG_PREFIX, retrieveHttp

get_env = get_store_reader()


def execute(an_id):
    url = f"{get_env('SHOPPING_SERVICE_URL')}/products/{an_id}"
    data = retrieveHttp(url)({
        LOG_PREFIX: 'Get product',
    })
    assert data is not None
    return data

