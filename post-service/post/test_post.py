import pytest

from lib.config import get_store_reader_low_case
from lib.driver import get_driver_from_folder

get_env_low_case = get_store_reader_low_case()
get_driver = get_driver_from_folder('post-service.post.')


def test_post():
    data = get_driver('post')('1')
    assert data is not None
    assert data.get('id', None) == '1'
    assert len(data.get('title', 'None')) > 0
    assert len(data.get('body', 'None')) > 0


@pytest.mark.skipif(
    get_env_low_case('DRIVER') == 'post-service-2',
    reason="Post-Service-2 cannot do a second post")
def test_post_second():
    data = get_driver('post')('2')
    assert data is not None
    assert data.get('id', None) == '2'
    assert len(data.get('title', 'None')) > 0
    assert len(data.get('body', 'None')) > 0
