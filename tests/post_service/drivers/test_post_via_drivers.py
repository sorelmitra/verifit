import pytest
from verifit.prop import get_prop, get_defaulted_prop

from src.verifit.driver import driver_is_one_of
from tests.post_service.drivers.drivers import DRIVER_BAR
from tests.post_service.drivers.dsl_post import post


@pytest.mark.skipif(driver_is_one_of([DRIVER_BAR]), reason='bar cannot post')
def test_post_with_drivers():
    payload = {
        "userId": '2',
        "title": "test post",
        "body": "test post body"
    }
    data = post(payload)
    assert data is not None
    assert get_prop(data)('userId') == '2'
    assert len(get_defaulted_prop(data)('title')('')) > 0
    assert len(get_defaulted_prop(data)('body')('')) > 0
