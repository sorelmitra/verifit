from datetime import datetime
import pytest

from verifit.config import get_store_writer
from verifit.login import ACCESS_TOKEN, EXPIRY_DATE, LOGIN_DATA

from driver_post_all import all_post_drivers


set_env = get_store_writer()

def simulate_login():
    # We're simulating login because our test GraphQL server doesn't have
    # login and we wanna showcase using our auth helper for GraphQL
    set_env(LOGIN_DATA)({
        ACCESS_TOKEN: 'dummy token',
        EXPIRY_DATE: datetime.now()
    })


def test_post(select_current_post_driver):
    simulate_login()
    post_driver = select_current_post_driver(all_post_drivers())
    data = post_driver('1')
    assert data is not None
    assert data.get('id', None) == '1'
    assert len(data.get('title', 'None')) > 0
    assert len(data.get('body', 'None')) > 0


@pytest.mark.skip_drivers([
    {'name': 'baz', 'reason': 'Cannot do a second post via baz'}
])
def test_post_second(select_current_post_driver):
    simulate_login()
    post_driver = select_current_post_driver(all_post_drivers())
    data = post_driver('2')
    assert data is not None
    assert data.get('id', None) == '2'
    assert len(data.get('title', 'None')) > 0
    assert len(data.get('body', 'None')) > 0
