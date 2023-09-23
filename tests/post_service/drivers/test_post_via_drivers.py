import pytest

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
    assert data.get('userId') == '2'
    assert len(data.get('title', '')) > 0
    assert len(data.get('body', '')) > 0
