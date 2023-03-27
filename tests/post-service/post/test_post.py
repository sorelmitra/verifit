from datetime import datetime
import pytest
from verifit.config import get_store_writer

from verifit.driver import get_driver
from verifit.login import ACCESS_TOKEN, EXPIRY_DATE, LOGIN_DATA

set_env = get_store_writer()


def simulate_login():
    # We're simulating login because our test GraphQL server doesn't have
    # login and we wanna showcase using our auth helper for GraphQL
    set_env(LOGIN_DATA)({
        ACCESS_TOKEN: 'dummy token',
        EXPIRY_DATE: datetime.now()
    })


def test_post(post_driver_name):
    simulate_login()
    data = get_driver(post_driver_name)('post')('1')
    assert data is not None
    assert data.get('id', None) == '1'
    assert len(data.get('title', 'None')) > 0
    assert len(data.get('body', 'None')) > 0


@pytest.mark.skip_drivers([
    {'name': 'post-service-2', 'reason': 'Cannot do a second post via GraphQL'}
])
def test_post_second(post_driver_name):
    simulate_login()
    data = get_driver(post_driver_name)('post')('2')
    assert data is not None
    assert data.get('id', None) == '2'
    assert len(data.get('title', 'None')) > 0
    assert len(data.get('body', 'None')) > 0
