import importlib
import inspect
import os
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


def get_driver_params(env_var, default_values):
    requested_drivers = get_env(env_var)
    if requested_drivers is not None:
        return requested_drivers.split(',')
    return default_values


def get_driver(request):
    driver_to_skip = get_marker(request)('skip_driver')
    if driver_to_skip == request.param:
        pytest.skip('skipped for this driver: {}'.format(driver_to_skip))

    functionality_name = get_marker(request)('driver_functionality')
    functionality = f"{request.param}_{functionality_name}"
    return import_functionality(functionality)


def get_functionality_per_driver(driver_instance):
    def with_functionality_name(name):
        module = inspect.getmodule(driver_instance)
        name_parts = module.__name__.split('_')
        functionality = f"{name_parts[0]}_{name}"
        return import_functionality(functionality)
    return with_functionality_name


def import_functionality(functionality):
    def import_functionality_from_current_folder(functionality):
        print(f"Getting functionality {functionality}")
        module = importlib.import_module(functionality)
        return module.execute

    def get_test_directories():
        initial_path = '.'
        ignore_pattern = r"^(\..+)|(__pycache__)|(lib)$"
        ignore_root_pattern = r"^(\./\..+)|(lib)$"
        found_paths = []
        for path in initial_path:
            for root, directories, files in os.walk(path):
                for dir_name in directories:
                    relative_path = os.path.join(root, dir_name)
                    # print('XXXXXXXX', root, dir_name)
                    if re.match(ignore_pattern, dir_name):
                        continue
                    if re.match(ignore_root_pattern, root):
                        continue
                    found_paths.append(relative_path)
        # print('XXXXXXXX', 'found_paths')
        return found_paths

    def import_functionality_from_path(functionality, found_path):
        relative_path = re.sub(r"^[^/]*/", '', found_path)
        package_path = re.sub(r"/", '.', relative_path)
        # print('XXXXXXXX', 'package_path', package_path)
        current_path_functionality = f"{package_path}.{functionality}"
        try:
            print(f"Getting functionality {current_path_functionality} ... ", end='')
            module = importlib.import_module(current_path_functionality)
            print('Ok.')
            return module.execute
        except ModuleNotFoundError:
            print(f"not found.")
            return None

    try:
        return import_functionality_from_current_folder(functionality)
    except ModuleNotFoundError:
        found_paths = get_test_directories()
        for found_path in found_paths:
            func = import_functionality_from_path(functionality, found_path)
            if func:
                return func
        raise Exception(f"Failed to load module {functionality}, searched in {found_paths}")
