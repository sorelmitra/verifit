import pytest


@pytest.mark.driver_functionality('post')
def test_post(post_driver):
    data = post_driver('1')
    assert data is not None
    assert data.get('id', None) == '1'
    assert len(data.get('title', 'None')) > 0
    assert len(data.get('body', 'None')) > 0


@pytest.mark.skip_driver('post-service-2')
@pytest.mark.driver_functionality('post')
def test_post_second(post_driver):
    data = post_driver('2')
    assert data is not None
    assert data.get('id', None) == '2'
    assert len(data.get('title', 'None')) > 0
    assert len(data.get('body', 'None')) > 0
