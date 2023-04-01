import re

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


def select_driver(driver_name):
    def with_drivers(drivers):
        matched_driver = None
        for driver in drivers:
            if re.match(rf"driver.+{driver_name}", driver.__name__) is not None:
                if matched_driver is not None:
                    raise Exception(f"More than one driver matches <{driver_name}>: <{matched_driver.__name__}>, and <{driver.__name__}>")
                matched_driver = driver
        if matched_driver is not None:
            return matched_driver
        raise Exception(f"Could not find driver with name <{driver_name}>" + \
            ' in the list of drivers:\n' + \
            '\n'.join(map(lambda d: d.__name__, drivers)) + \
            '\n')
    return with_drivers
