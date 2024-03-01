from functools import cache
from multiprocessing import Process
import time
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


@cache
def get_store():
    return {}


@api().route(endpoint(), methods=['POST'])
def webhook_observer():
    store = get_store()
    q = store.get(KEY_QUEUE)
    webhook_response = request.json
    print(f"Payload: {webhook_response}")
    q.put(webhook_response)
    return json.dumps({"success": True}), 200


def start_webhook_observer(q):
    store = get_store()
    store[KEY_QUEUE] = q
    api().run(port=port())


def webhook_server_start(q):
    server = Process(target=start_webhook_observer, args=(q,))
    server.start()
    time.sleep(3)
    return server
