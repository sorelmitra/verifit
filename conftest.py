from lib.config import get_store_reader, get_store_reader_low_case

get_env = get_store_reader()
get_env_low_case = get_store_reader_low_case()


def pytest_collection_finish():
    """
    Called after collection of tests has finished.
    """
    env = get_env('ENV')
    driver = get_env_low_case('DRIVER')
    driver_show = ""
    if driver is not None:
        driver_show = f"DRIVER={driver}"
    print(f"ENV={env} {driver_show}")
