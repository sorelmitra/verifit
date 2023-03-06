import pytest

from src.lib.driver import get_driver_params, get_driver


@pytest.fixture(params=get_driver_params('POST_DRIVER', ['post-service-1', 'post-service-2']))
def post_driver(request):
    return get_driver(request)


@pytest.fixture(params=get_driver_params('SHOPPING_DRIVER', ['shopping-service']))
def shopping_driver(request):
    return get_driver(request)
