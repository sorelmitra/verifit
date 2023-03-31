import pytest

from verifit.driver import get_driver_name, get_driver_params, select_driver


@pytest.fixture(params=get_driver_params('POST_DRIVER')(['bar', 'baz']))
def select_current_post_driver(request):
    return select_driver(get_driver_name(request))


@pytest.fixture(params=get_driver_params('SHOPPING_DRIVER')(['foo']))
def select_current_shopping_driver(request):
    return select_driver(get_driver_name(request))
