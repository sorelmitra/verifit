import importlib

import pytest

from lib.config import get_store_reader

get_env = get_store_reader()


def get_marker(request):
    def with_value(value):
        marker = request.node.get_closest_marker(value)
        if marker is None:
            return None
        return marker.args[0]
    return with_value


def get_post_driver_params():
    requested_drivers = get_env('POST_DRIVER')
    if requested_drivers is not None:
        return requested_drivers.split(',')
    return ['post-service-1', 'post-service-2']


@pytest.fixture(params=get_post_driver_params())
def post_driver(request):
    driver_to_skip = get_marker(request)('skip_driver')
    if driver_to_skip == request.param:
        pytest.skip('skipped for this driver: {}'.format(driver_to_skip))

    functionality = get_marker(request)('driver_functionality')
    module = importlib.import_module(f"{request.param}_{functionality}")
    return module.execute


def get_shopping_driver_params():
    requested_drivers = get_env('SHOPPING_DRIVER')
    if requested_drivers is not None:
        return requested_drivers.split(',')
    return ['shopping-service']


@pytest.fixture(params=get_shopping_driver_params())
def shopping_driver(request):
    functionality = get_marker(request)('driver_functionality')
    module = importlib.import_module(f"{request.param}_{functionality}")
    return module.execute
