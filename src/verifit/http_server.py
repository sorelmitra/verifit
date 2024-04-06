from functools import cache
from multiprocessing import Process
import time
import queue
from flask import Flask, request, json


@cache
def api():
    return Flask('webhook-observer-server')


class HttpConfig:
    PORT = 5768
    POST_PATH = '/create'
    GET_PATH = '/obtain'
    PUT_PATH = '/update'
    PATCH_PATH = '/patch'
    DELETE_PATH = '/delete'

    @staticmethod
    def base_url():
        return f"http://localhost:{HttpConfig.PORT}"

    @staticmethod
    def post_url():
        return f"{HttpConfig.base_url()}{HttpConfig.POST_PATH}"

    @staticmethod
    def get_url():
        return f"{HttpConfig.base_url()}{HttpConfig.GET_PATH}"

    @staticmethod
    def put_url():
        return f"{HttpConfig.base_url()}{HttpConfig.PUT_PATH}"

    @staticmethod
    def patch_url():
        return f"{HttpConfig.base_url()}{HttpConfig.PATCH_PATH}"

    @staticmethod
    def delete_url():
        return f"{HttpConfig.base_url()}{HttpConfig.DELETE_PATH}"


KEY_QUEUE = 'queue'
KEY_CALLS_COUNT = 'calls_count'
KEY_STATUS_TO_RETURN = 'status_to_return'
KEY_SUCCEED_AT_ATTEMPT_NO = 'succeed_at_attempt_no'


@cache
def get_store():
    return {}


class EndpointResult:
    def __init__(self, *, success, status_code, response_data):
        self.success = success
        self.status_code = status_code
        self.response_data = response_data


def determine_endpoint_result() -> EndpointResult:
    store = get_store()
    status_to_return = store.get(KEY_STATUS_TO_RETURN)
    succeed_at_attempt_no = store.get(KEY_SUCCEED_AT_ATTEMPT_NO)
    calls_count = store.get(KEY_CALLS_COUNT)
    calls_count = calls_count + 1
    store[KEY_CALLS_COUNT] = calls_count
    if succeed_at_attempt_no > 0:
        if calls_count >= succeed_at_attempt_no:
            status_to_return = 202
    success = 200 <= status_to_return <= 299
    response = {"success": success}
    return EndpointResult(
        success=success, status_code=status_to_return, response_data=response)


@api().route(HttpConfig.POST_PATH, methods=['POST'])
def post_listener():
    store = get_store()
    q = store.get(KEY_QUEUE)
    post_response = request.json
    print(f"Payload: {post_response}")
    endpoint_result = determine_endpoint_result()
    q.put(post_response if endpoint_result.success else endpoint_result.response_data)
    return json.dumps(endpoint_result.response_data), endpoint_result.status_code


@api().route(HttpConfig.GET_PATH, methods=['GET'])
def get_listener():
    store = get_store()
    q = store.get(KEY_QUEUE)
    endpoint_result = determine_endpoint_result()
    q.put(endpoint_result.response_data)
    return json.dumps(endpoint_result.response_data), endpoint_result.status_code


@api().route(HttpConfig.PUT_PATH, methods=['PUT'])
def put_listener():
    store = get_store()
    q = store.get(KEY_QUEUE)
    put_response = request.json
    print(f"Payload: {put_response}")
    endpoint_result = determine_endpoint_result()
    q.put(put_response if endpoint_result.success else endpoint_result.response_data)
    return json.dumps(endpoint_result.response_data), endpoint_result.status_code


@api().route(HttpConfig.PATCH_PATH, methods=['PATCH'])
def patch_listener():
    store = get_store()
    q = store.get(KEY_QUEUE)
    patch_response = request.json
    print(f"Payload: {patch_response}")
    endpoint_result = determine_endpoint_result()
    q.put(patch_response if endpoint_result.success else endpoint_result.response_data)
    return json.dumps(endpoint_result.response_data), endpoint_result.status_code


@api().route(HttpConfig.DELETE_PATH, methods=['DELETE'])
def delete_listener():
    store = get_store()
    q = store.get(KEY_QUEUE)
    endpoint_result = determine_endpoint_result()
    q.put(endpoint_result.response_data)
    return json.dumps(endpoint_result.response_data), endpoint_result.status_code


def http_server_start_process(response_queue, status_to_return, succeed_at_attempt_no):
    store = get_store()
    store[KEY_QUEUE] = response_queue
    store[KEY_CALLS_COUNT] = 0
    store[KEY_STATUS_TO_RETURN] = status_to_return
    store[KEY_SUCCEED_AT_ATTEMPT_NO] = succeed_at_attempt_no
    api().run(port=HttpConfig.PORT)


def http_server_start(*, response_queue, status=200, succeed_at_attempt_no=0):
    server = Process(
        target=http_server_start_process,
        args=(response_queue, status, succeed_at_attempt_no))
    server.start()
    time.sleep(2)
    return server


def http_server_stop(server):
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
