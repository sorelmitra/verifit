import pytest
from verifit.config import get_store_reader
from verifit.web_sockets import IGNORE_LIST, SERVER, ws_send_and_receive

get_env = get_store_reader()


@pytest.mark.skip(reason="The demo WSS server no longer accepts the API key")
def test_echo_service():
    data = ws_send_and_receive(config={
        SERVER: get_env('ECHO_SERVICE_URL'),
        IGNORE_LIST: ['ping', 'Hello world!']
    })(data={
        "user": "echo-user",
        "message": "Hi from the tests!"
    })
    assert data is not None
    assert data.get('user', None) == 'echo-user'
    assert data.get('message', None) == 'Hi from the tests!'