from src.verifit.driver import call_driver
from tests.post_service.drivers.driver_foo import foo_post
from tests.post_service.drivers.drivers import DRIVER_FOO


def post(payload):
    return call_driver({
        DRIVER_FOO: foo_post,
    })(payload)
