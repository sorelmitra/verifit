from functools import cache
import json
import multiprocessing
import requests

from verifit.web_hooks import webhook_server_start, webhook_url


KEY_CALLBACKS = 'callbacks'

#
# The 'app to test'
# Dummy app that pushes a notice via Web Hooks
#

@cache
def notice_observers_store():
    return {}


def notice_register_observer(*, event, url):
    store = notice_observers_store()
    callbacks = store.get(event, [])
    callbacks.append(url)
    store[event] = callbacks


def notice_process_event(name):
    store = notice_observers_store()
    callbacks = store.get(name, None)
    if callbacks is None:
        return
    for url in callbacks:
        payload = {
            "notice": name,
            "payload": {
                "aString": "hey",
                "aNumber": 7
            }
        }
        print(f"Sending notice {name} to {url}")
        resp = requests.post(url=url, data=json.dumps(payload), headers={
            'Content-Type': 'application/json'
        }, timeout=3)
        assert 200 <= resp.status_code <= 299


# The test

def test_send_notice():
    # Start the WebHook server, that offers a endpoint for receiving the hook data
    q = multiprocessing.Queue()
    server = webhook_server_start(q)

    # Register the WebHook endpoint in our dummy notice app
    notice_register_observer(event='foo', url=webhook_url())
    
    # Trigger the WebHook event in the dummy notice app
    notice_process_event('foo')
    
    # Stop the WebHook server
    server.terminate()
    server.join()
    server.close()
    
    # Verify the WebHook event that was received
    webhook_response = q.get()
    assert webhook_response == {
        "payload": {
            "aString": "hey",
            "aNumber": 7
        },
        "notice": "foo",
    }

