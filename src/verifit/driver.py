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


def get_driver_params(env_var):
    def with_default_values(default_values):
        requested_drivers = get_env(env_var)
        if requested_drivers is not None:
            return requested_drivers.split(',')
        return default_values
    return with_default_values


def get_driver_name(request):
    drivers_to_skip = get_marker(request)('skip_drivers') or []
    for driver_to_skip in drivers_to_skip:
        name = driver_to_skip.get('name', None)
        reason = driver_to_skip.get('reason', 'skipped for this driver: {}'.format(driver_to_skip))
        if name == request.param:
            pytest.skip(reason)
            break
    return request.param


def get_driver(name):
    def with_functionality(functionality_name):
        functionality = f"{name}_{functionality_name}"
        return importlib.import_module(functionality).execute
    return with_functionality
