from verifit.driver import call_driver
from tests.post_service.drivers.driver_bar import bar_post, bar_check_post_response
from tests.post_service.drivers.driver_foo import foo_post, foo_check_post_response
from tests.post_service.drivers.drivers import DRIVER_FOO, DRIVER_BAR


def post(**kwargs):
    return call_driver({
        DRIVER_FOO: foo_post,
        DRIVER_BAR: bar_post,
    })(**kwargs)


def check_post_response(**kwargs):
    return call_driver({
        DRIVER_FOO: foo_check_post_response,
        DRIVER_BAR: bar_check_post_response,
    })(**kwargs)
