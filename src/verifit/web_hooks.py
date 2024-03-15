from functools import cache
from multiprocessing import Process
import time
import queue
from flask import Flask, request, json


@cache
def api():
    return Flask('webhook-observer-server')


@cache
def port():
    return 5768


@cache
def endpoint():
    return '/webhook'


@cache
def webhook_url():
    return f"http://localhost:{port()}{endpoint()}"


KEY_QUEUE = 'queue'
KEY_CALLS_COUNT = 'calls_count'
KEY_STATUS_TO_RETURN = 'status_to_return'
KEY_SUCCEED_AT_ATTEMPT_NO = 'succeed_at_attempt_no'


@cache
def get_store():
    return {}


@api().route(endpoint(), methods=['POST'])
def webhook_observer():
    store = get_store()
    q = store.get(KEY_QUEUE)
    webhook_response = request.json
    print(f"Payload: {webhook_response}")
    status_to_return = store.get(KEY_STATUS_TO_RETURN)
    succeed_at_attempt_no = store.get(KEY_SUCCEED_AT_ATTEMPT_NO)
    calls_count = store.get(KEY_CALLS_COUNT)
    calls_count = calls_count + 1
    store[KEY_CALLS_COUNT] = calls_count
    if succeed_at_attempt_no > 0:
        if calls_count >= succeed_at_attempt_no:
            status_to_return = 202
    success = 200 <= status_to_return <= 299
    local_response = {"success": success}
    q.put(webhook_response if success else local_response)
    return json.dumps(local_response), status_to_return


def start_webhook_observer(q, s, a):
    store = get_store()
    store[KEY_QUEUE] = q
    store[KEY_CALLS_COUNT] = 0
    store[KEY_STATUS_TO_RETURN] = s
    store[KEY_SUCCEED_AT_ATTEMPT_NO] = a
    api().run(port=port())


def webhook_server_start(*, queue, status=200, succeed_at_attempt_no=0):
    server = Process(target=start_webhook_observer, args=(queue, status, succeed_at_attempt_no))
    server.start()
    time.sleep(2)
    return server


def webhook_server_stop(server):
    server.terminate()
    server.join()
    server.close()


def queue_is_empty(q):
    try:
        q.get(timeout=1)
        return False
    except queue.Empty:
        return True
    except:
        assert False
