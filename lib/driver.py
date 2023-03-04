import importlib

from lib.config import get_store_reader

get_env = get_store_reader()


def get_driver_from_folder(folder):
    def with_functionality(functionality):
        driver_pool_name = get_env('DRIVER')
        module = importlib.import_module(f"{folder}{driver_pool_name}_{functionality}")
        return module.execute
    return with_functionality


def get_driver(functionality):
    return get_driver_from_folder('')(functionality)
