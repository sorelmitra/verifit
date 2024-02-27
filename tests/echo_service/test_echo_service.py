import pytest
from verifit.config import get_env_reader
from verifit.web_sockets import ws_send_and_receive

get_env = get_env_reader()


def test_echo_service():
    data = ws_send_and_receive(server=get_env('ECHO_SERVICE_URL'), ignore_list=['ping', 'Hello world!'],
                               data={
                                   "user": "echo-user",
                                   "message": "Hi from the tests!"
                               })
    assert data is not None
    assert data.get('user', None) == 'echo-user'
    assert data.get('message', None) == 'Hi from the tests!'
