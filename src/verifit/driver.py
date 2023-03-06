import importlib

import pytest

from .config import get_store_reader

get_env = get_store_reader()


def get_marker(request):
    def with_value(value):
        marker = request.node.get_closest_marker(value)
        if marker is None:
            return None
        return marker.args[0]
    return with_value


def get_driver_params(env_var, default_values):
    requested_drivers = get_env(env_var)
    if requested_drivers is not None:
        return requested_drivers.split(',')
    return default_values


def get_driver(request):
    driver_to_skip = get_marker(request)('skip_driver')
    if driver_to_skip == request.param:
        pytest.skip('skipped for this driver: {}'.format(driver_to_skip))

    functionality = get_marker(request)('driver_functionality')
    module = importlib.import_module(f"{request.param}_{functionality}")
    return module.execute
