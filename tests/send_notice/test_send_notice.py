from functools import cache
import json
import multiprocessing
import requests

from verifit.web_hooks import webhook_server_start, webhook_url, queue_is_empty


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
        for _ in range(0, 3):
            resp = requests.post(url=url, data=json.dumps(payload), headers={
                'Content-Type': 'application/json'
            }, timeout=1)
            if 200 <= resp.status_code <= 299:
                break
        return resp.status_code


# The tests

def test_send_notice_succeeds():
    # Start the WebHook server, that offers a endpoint for receiving the hook data
    q = multiprocessing.Queue()
    server = webhook_server_start(queue=q)

    # Register the WebHook endpoint in our dummy notice app
    notice_register_observer(event='foo', url=webhook_url())
    
    # Trigger the WebHook event in the dummy notice app
    status = notice_process_event('foo')
    
    # Stop the WebHook server
    server.terminate()
    server.join()
    server.close()
    
    # Check the results, must be done after stopping the server
    assert status == 200
    webhook_response = q.get(timeout=1)
    assert webhook_response == {
        "payload": {
            "aString": "hey",
            "aNumber": 7
        },
        "notice": "foo",
    }


def test_send_notice_fails():
    # Start the WebHook server, that offers a endpoint for receiving the hook data
    q = multiprocessing.Queue()
    server = webhook_server_start(queue=q, status=406)

    # Register the WebHook endpoint in our dummy notice app
    notice_register_observer(event='foo', url=webhook_url())
    
    # Trigger the WebHook event in the dummy notice app
    status = notice_process_event('foo')
    
    # Stop the WebHook server
    server.terminate()
    server.join()
    server.close()
    
    # Check the results, must be done after stopping the server
    assert status == 406
    for _ in range(0, 3):
        webhook_response = q.get(timeout=1)
        assert webhook_response == { "success": False }
    assert queue_is_empty(q)


def test_send_notice_second_attempt_succeeds():
    # Start the WebHook server, that offers a endpoint for receiving the hook data
    q = multiprocessing.Queue()
    server = webhook_server_start(queue=q, status=406, succeed_at_attempt_no=2)

    # Register the WebHook endpoint in our dummy notice app
    notice_register_observer(event='foo', url=webhook_url())
    
    # Trigger the WebHook event in the dummy notice app
    status = notice_process_event('foo')
    
    # Stop the WebHook server
    server.terminate()
    server.join()
    server.close()
    
    # Check the results, must be done after stopping the server
    assert status == 202  # our helper webhook server returns 202 if it succeeds after a failure
    # First attempt fails
    webhook_response = q.get(timeout=1)
    assert webhook_response == { "success": False }
    # Second attempt succeeds
    webhook_response = q.get(timeout=1)
    assert webhook_response == {
        "payload": {
            "aString": "hey",
            "aNumber": 7
        },
        "notice": "foo",
    }
    # No further calls to our webhook server
    assert queue_is_empty(q)

