import pytest

from verifit.driver import get_driver


def test_post(post_driver_name):
    data = get_driver(post_driver_name)('post')('1')
    assert data is not None
    assert data.get('id', None) == '1'
    assert len(data.get('title', 'None')) > 0
    assert len(data.get('body', 'None')) > 0


@pytest.mark.skip_drivers([
    {'name': 'post-service-2', 'reason': 'Cannot do a second post via GraphQL'}
])
def test_post_second(post_driver_name):
    data = get_driver(post_driver_name)('post')('2')
    assert data is not None
    assert data.get('id', None) == '2'
    assert len(data.get('title', 'None')) > 0
    assert len(data.get('body', 'None')) > 0
