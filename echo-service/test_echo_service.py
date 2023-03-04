from config import get_store_reader
from web_sockets import ws_send_and_receive

get_env = get_store_reader()


def test_echo_service():
    data = ws_send_and_receive({
      "user": "echo-user",
      "message": "Hi from the tests!"
    })(get_env('ECHO_SERVICE_URL'))(['ping', 'Hello world!'])
    assert data is not None
    assert data.get('user', None) == 'echo-user'
    assert data.get('message', None) == 'Hi from the tests!'
