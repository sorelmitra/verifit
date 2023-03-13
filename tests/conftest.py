import pytest

from verifit.driver import get_driver_name, get_driver_params


@pytest.fixture(params=get_driver_params('POST_DRIVER', ['post-service-1', 'post-service-2']))
def post_driver_name(request):
    return get_driver_name(request)


@pytest.fixture(params=get_driver_params('SHOPPING_DRIVER', ['shopping-service']))
def shopping_driver_name(request):
    return get_driver_name(request)
