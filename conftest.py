import sys

from lib.config import get_store_reader

sys.path.append("lib")

get_env = get_store_reader()


def pytest_collection_finish():
    """
    Called after collection of tests has finished.
    """
    env = get_env('ENV')
    print(f"ENV={env}")
