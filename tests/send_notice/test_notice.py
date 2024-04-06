from functools import cache
import json
import multiprocessing
import requests

from verifit.http_server import http_server_start, http_server_stop, HttpConfig, queue_is_empty


#
#
#
#
#
#
# Helper function
#
#
#
#
#
#


def launch_request(*, name, url, method=requests.get, payload=None):
    resp = None
    for i in range(0, 3):
        print(f"{method.__name__} notice {name} to {url}, attempt {i}")
        resp = method(
            url=url,
            data=None if payload is None else json.dumps(payload),
            headers={
                'Content-Type': 'application/json'
            },
            timeout=1
        )
        if 200 <= resp.status_code <= 299:
            break
    return resp.status_code


def send_notice_with_retries(url):
    name = 'foo'
    payload = {
        "notice": name,
        "payload": {
            "aString": "hey",
            "aNumber": 7
        }
    }
    print(f"Sending notice {name} to {url}")
    return launch_request(name=name, url=url, method=requests.post, payload=payload)


def get_notice_with_retries(url):
    name = 'foo'
    print(f"Getting notice {name} from {url}")
    return launch_request(name=name, url=url)


def put_notice_with_retries(url):
    name = 'foo'
    payload = {
        "notice": name,
        "payload": {
            "aString": "yo",
            "aNumber": 8
        }
    }
    print(f"Putting notice {name} to {url}")
    return launch_request(name=name, url=url, method=requests.put, payload=payload)


def patch_notice_with_retries(url):
    name = 'foo'
    payload = {
        "notice": name,
        "payload": {
            "aNumber": 9
        }
    }
    print(f"Patching notice {name} to {url}")
    return launch_request(name=name, url=url, method=requests.patch, payload=payload)


def delete_notice_with_retries(url):
    name = 'foo'
    print(f"Deleting notice {name} via {url}")
    return launch_request(name=name, url=url, method=requests.delete)


#
#
#
#
#
#
# WebHooks, i.e. HTTP POST, tests
#
#
#
#
#
#


def test_send_notice_succeeds():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q)

    try:
        status = send_notice_with_retries(HttpConfig.post_url())

        assert status == 200
        webhook_response = q.get(timeout=1)
        assert webhook_response == {
            "payload": {
                "aString": "hey",
                "aNumber": 7
            },
            "notice": "foo",
        }
    finally:
        http_server_stop(server)


def test_send_notice_fails():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q, status=406)

    try:
        status = send_notice_with_retries(HttpConfig.post_url())

        assert status == 406
        for _ in range(0, 3):
            webhook_response = q.get(timeout=1)
            assert webhook_response == { "success": False }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_send_notice_second_attempt_succeeds():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q, status=406, succeed_at_attempt_no=2)

    try:
        status = send_notice_with_retries(HttpConfig.post_url())

        # Our HTTP server returns 202 if it succeeds after a failure,
        # and the dummy app forwards it
        assert status == 202
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
    finally:
        http_server_stop(server)


#
#
#
#
#
#
# Tests for other HTTP methods
#
#
#
#
#
#

def test_get_notice_success():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q)

    try:
        status = get_notice_with_retries(HttpConfig.get_url())
        assert status == 200
        get_response = q.get(timeout=1)
        assert get_response == { "success": True }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_get_notice_second_attempt_succeeds():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q, status=406, succeed_at_attempt_no=2)

    try:
        status = get_notice_with_retries(HttpConfig.get_url())
        assert status == 202
        get_response = q.get(timeout=1)
        assert get_response == { "success": False }
        get_response = q.get(timeout=1)
        assert get_response == { "success": True }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_put_notice_success():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q)

    try:
        status = put_notice_with_retries(HttpConfig.put_url())
        assert status == 200
        put_response = q.get(timeout=1)
        assert put_response == {
            "notice": "foo",
            "payload": {
                "aString": "yo",
                "aNumber": 8
            }
        }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_put_notice_second_attempt_succeeds():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q, status=406, succeed_at_attempt_no=2)

    try:
        status = put_notice_with_retries(HttpConfig.put_url())
        assert status == 202
        put_response = q.get(timeout=1)
        assert put_response == { "success": False }
        put_response = q.get(timeout=1)
        assert put_response == {
            "notice": "foo",
            "payload": {
                "aString": "yo",
                "aNumber": 8
            }
        }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_patch_notice_success():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q)

    try:
        status = patch_notice_with_retries(HttpConfig.patch_url())
        assert status == 200
        patch_response = q.get(timeout=1)
        assert patch_response == {
            "notice": "foo",
            "payload": {
                "aNumber": 9
            }
        }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_patch_notice_second_attempt_succeeds():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q, status=406, succeed_at_attempt_no=2)

    try:
        status = patch_notice_with_retries(HttpConfig.patch_url())
        assert status == 202
        patch_response = q.get(timeout=1)
        assert patch_response == { "success": False }
        patch_response = q.get(timeout=1)
        assert patch_response == {
            "notice": "foo",
            "payload": {
                "aNumber": 9
            }
        }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_delete_notice_success():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q)

    try:
        status = delete_notice_with_retries(HttpConfig.delete_url())
        assert status == 200
        delete_response = q.get(timeout=1)
        assert delete_response == { "success": True }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_delete_notice_second_attempt_succeeds():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q, status=406, succeed_at_attempt_no=2)

    try:
        status = delete_notice_with_retries(HttpConfig.delete_url())
        assert status == 202
        delete_response = q.get(timeout=1)
        assert delete_response == { "success": False }
        delete_response = q.get(timeout=1)
        assert delete_response == { "success": True }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)
