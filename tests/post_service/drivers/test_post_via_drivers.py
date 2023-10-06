import pytest

from src.verifit.driver import driver_is_one_of
from tests.post_service.drivers.drivers import DRIVER_BAZ
from tests.post_service.drivers.dsl_post import post, check_post_response


@pytest.mark.skipif(driver_is_one_of([DRIVER_BAZ]), reason='bar cannot post')
def test_post_with_drivers():
    response = post(userId="2", title="a title", body="a body")
    check_post_response(response=response, userId="2")
