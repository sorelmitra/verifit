from verifit.config import get_store_reader

get_env = get_store_reader()


def get_driver():
    return get_env('DRIVER')


def call_driver(drivers):
    def with_arg(arg):
        driver = get_driver()
        if driver in drivers.keys():
            return drivers.get(driver)(arg)
    return with_arg


def driver_is_one_of(drivers):
    return get_driver() in drivers
