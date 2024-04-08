import json
import multiprocessing
import os
import requests

from functools import cache
from ariadne import load_schema_from_path, ObjectType, make_executable_schema, \
    snake_case_fallback_resolvers, convert_kwargs_to_snake_case

from verifit.http_server import http_server_start, http_server_stop, HttpConfig, queue_is_empty, EndpointResult
from verifit.retrieve import retrieve_graphql


#
#
#
#
#
#
# HTTP helper functions
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
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406, response_data={"reason": f"foo error {i}"})
            for i in range(0, 3)
        ]
    )

    try:
        send_notice_with_retries(HttpConfig.post_url())

        for i in range(0, 3):
            webhook_response = q.get(timeout=1)
            assert webhook_response == {"reason": f"foo error {i}"}
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_send_notice_second_attempt_succeeds_default_response():
    q = multiprocessing.Queue()
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406, response_data={"reason": f"foo error"})
        ]
    )

    try:
        status = send_notice_with_retries(HttpConfig.post_url())

        # Our HTTP server returns 202 if it succeeds after a failure,
        # and the dummy app forwards it
        assert status == 202
        # First attempt fails
        webhook_response = q.get(timeout=1)
        assert webhook_response == {"reason": f"foo error"}
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


def test_send_notice_second_attempt_succeeds_custom_response():
    q = multiprocessing.Queue()
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406, response_data={"reason": f"foo error"}),
            EndpointResult(status_code=203, response_data={"foo": "bar"})
        ]
    )

    try:
        status = send_notice_with_retries(HttpConfig.post_url())

        # Our HTTP server returns 202 if it succeeds after a failure,
        # and the dummy app forwards it
        assert status == 202
        # First attempt fails
        webhook_response = q.get(timeout=1)
        assert webhook_response == {"reason": f"foo error"}
        # Second attempt succeeds
        webhook_response = q.get(timeout=1)
        assert webhook_response == {"foo": "bar"}
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
# HTTP GET tests
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
        assert get_response == {"success": True}
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_get_notice_second_attempt_succeeds_default_response():
    q = multiprocessing.Queue()
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406, response_data={"reason": f"foo error"})
        ]
    )

    try:
        status = get_notice_with_retries(HttpConfig.get_url())
        assert status == 202
        get_response = q.get(timeout=1)
        assert get_response == {"reason": f"foo error"}
        get_response = q.get(timeout=1)
        assert get_response == {"success": True}
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_get_notice_second_attempt_succeeds_custom_response():
    q = multiprocessing.Queue()
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406, response_data={"reason": f"foo error"}),
            EndpointResult(status_code=203, response_data={"foo": "bar"})
        ]
    )

    try:
        status = get_notice_with_retries(HttpConfig.get_url())
        assert status == 202
        get_response = q.get(timeout=1)
        assert get_response == {"reason": f"foo error"}
        get_response = q.get(timeout=1)
        assert get_response == {"foo": "bar"}
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


#
#
#
#
#
#
# HTTP PUT tests
#
#
#
#
#
#


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


def test_put_notice_second_attempt_succeeds_default_response():
    q = multiprocessing.Queue()
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406, response_data={"reason": f"foo error"})
        ]
    )

    try:
        status = put_notice_with_retries(HttpConfig.put_url())
        assert status == 202
        put_response = q.get(timeout=1)
        assert put_response == {"reason": f"foo error"}
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


def test_put_notice_second_attempt_succeeds_custom_response():
    q = multiprocessing.Queue()
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406, response_data={"reason": f"foo error"}),
            EndpointResult(status_code=203, response_data={"foo": "bar"})
        ]
    )

    try:
        status = put_notice_with_retries(HttpConfig.put_url())
        assert status == 202
        put_response = q.get(timeout=1)
        assert put_response == {"reason": f"foo error"}
        put_response = q.get(timeout=1)
        assert put_response == {"foo": "bar"}
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


#
#
#
#
#
#
# HTTP PATCH tests
#
#
#
#
#
#


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


def test_patch_notice_second_attempt_succeeds_default_response():
    q = multiprocessing.Queue()
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406, response_data={"reason": f"foo error"})
        ]
    )

    try:
        status = patch_notice_with_retries(HttpConfig.patch_url())
        assert status == 202
        patch_response = q.get(timeout=1)
        assert patch_response == {"reason": f"foo error"}
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


def test_patch_notice_second_attempt_succeeds_custom_response():
    q = multiprocessing.Queue()
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406, response_data={"reason": f"foo error"}),
            EndpointResult(status_code=203, response_data={"foo": "bar"})
        ]
    )

    try:
        status = patch_notice_with_retries(HttpConfig.patch_url())
        assert status == 202
        patch_response = q.get(timeout=1)
        assert patch_response == {"reason": f"foo error"}
        patch_response = q.get(timeout=1)
        assert patch_response == {"foo": "bar"}
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


#
#
#
#
#
#
# HTTP DELETE tests
#
#
#
#
#
#


def test_delete_notice_success():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q)

    try:
        status = delete_notice_with_retries(HttpConfig.delete_url())
        assert status == 200
        delete_response = q.get(timeout=1)
        assert delete_response == {"success": True}
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_delete_notice_second_attempt_succeeds_default_response():
    q = multiprocessing.Queue()
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406, response_data={"reason": f"foo error"})
        ]
    )

    try:
        status = delete_notice_with_retries(HttpConfig.delete_url())
        assert status == 202
        delete_response = q.get(timeout=1)
        assert delete_response == {"reason": f"foo error"}
        delete_response = q.get(timeout=1)
        assert delete_response == {"success": True}
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_delete_notice_second_attempt_succeeds_custom_response():
    q = multiprocessing.Queue()
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406, response_data={"reason": f"foo error"}),
            EndpointResult(status_code=203, response_data={"foo": "bar"})
        ]
    )

    try:
        status = delete_notice_with_retries(HttpConfig.delete_url())
        assert status == 202
        delete_response = q.get(timeout=1)
        assert delete_response == {"reason": f"foo error"}
        delete_response = q.get(timeout=1)
        assert delete_response == {"foo": "bar"}
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


#
#
#
#
#
#
# Tests for GraphQL
#
#
#
#
#
#


def launch_graphql_get_notice(notice_id: str):
    response = retrieve_graphql(
        url=HttpConfig.graphql_url(),
        query="""
                query GET_NOTICE($id: ID!) {
                    getNotice(id: $id) {
                        notice {
                            id
                            title
                        }
                        success
                        errors
                    }
                }
            """,
        variables={
            "id": notice_id
        },
        log_prefix='GraphQL Get Notice',
    )
    return response


def launch_graphql_create_notice(title: str):
    response = retrieve_graphql(
        url=HttpConfig.graphql_url(),
        query="""
                mutation CREATE_NOTICE($title: String!) {
                    createNotice(title: $title) {
                        notice {
                            id
                            title
                        }
                        success
                        errors
                    }
                }
            """,
        variables={
            "title": title
        },
        log_prefix='GraphQL Create Notice',
    )
    return response


def test_get_notice_graphql_succeeds():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q)

    try:
        response = launch_graphql_get_notice('foo')
        assert response == {
            "data": {
                "getNotice": {
                    "success": True,
                    "errors": None,
                    "notice": {
                        "id": 'foo',
                        "title": 'foo notice'
                    }
                }
            }
        }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_get_notice_graphql_second_attempt_succeeds():
    q = multiprocessing.Queue()
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406, response_data=f"foo error")
        ]
    )

    try:
        response = launch_graphql_get_notice('foo')
        assert response == {
            "data": {
                "getNotice": {
                    "success": False,
                    "errors": ["foo error"],
                    "notice": None
                }
            }
        }
        response = launch_graphql_get_notice('foo')
        assert response == {
            "data": {
                "getNotice": {
                    "success": True,
                    "errors": None,
                    "notice": {
                        "id": 'foo',
                        "title": 'foo notice'
                    }
                }
            }
        }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_create_notice_graphql_succeeds():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q)

    try:
        response = launch_graphql_create_notice('foo notice')
        assert response == {
            "data": {
                "createNotice": {
                    "success": True,
                    "errors": None,
                    "notice": {
                        "id": 'foo',
                        "title": 'foo notice'
                    }
                }
            }
        }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_create_notice_graphql_second_attempt_succeeds():
    q = multiprocessing.Queue()
    server = http_server_start(
        response_queue=q,
        endpoint_results=[
            EndpointResult(status_code=406)
        ]
    )

    try:
        response = launch_graphql_create_notice('foo notice')
        assert response == {
            "data": {
                "createNotice": {
                    "success": False,
                    "errors": ["Notice item not created"],
                    "notice": None
                }
            }
        }
        response = launch_graphql_create_notice('foo notice')
        assert response == {
            "data": {
                "createNotice": {
                    "success": True,
                    "errors": None,
                    "notice": {
                        "id": 'foo',
                        "title": 'foo notice'
                    }
                }
            }
        }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


#
#
#
#
#
#
# Tests for Custom GraphQL Schema
#
#
#
#
#
#


should_succeed = True


@cache
def test_store():
    return {}


@convert_kwargs_to_snake_case
def get_my_notice_resolver(_obj, _info, id):
    if should_succeed:
        payload = {
            "success": True,
            "my_notice": {
                "id": 'foo',
                "title": 'my foo notice'
            }
        }
    else:
        payload = {
            "success": False,
            "errors": [f"Notice item matching {id} not found"]
        }
    print(f"GraphQL Get Notice My Payload: {payload}")
    return payload


@convert_kwargs_to_snake_case
def create_my_notice_resolver(_obj, _info, title):
    if should_succeed:
        test_store()['title'] = title
        payload = {
            "success": True,
            "my_notice": {
                "id": 'foo',
                "title": title
            }
        }
    else:
        payload = {
            "success": False,
            "errors": [f"My notice item not created"]
        }
    print(f"GraphQL Create My Notice Payload: {payload}")
    return payload


def my_graphql_schema():
    type_definitions = load_schema_from_path(
        os.path.join(os.path.dirname(__file__), "my-schema.graphql"))

    query = ObjectType("Query")
    query.set_field("getMyNotice", get_my_notice_resolver)
    mutation = ObjectType("Mutation")
    mutation.set_field("createMyNotice", create_my_notice_resolver)

    return make_executable_schema(
        type_definitions, query, mutation, snake_case_fallback_resolvers
    )


def launch_graphql_get_my_notice(notice_id: str):
    response = retrieve_graphql(
        url=HttpConfig.graphql_url(),
        query="""
                query GET_MY_NOTICE($id: ID!) {
                    getMyNotice(id: $id) {
                        myNotice {
                            id
                            title
                        }
                        success
                        errors
                    }
                }
            """,
        variables={
            "id": notice_id
        },
        log_prefix='GraphQL Get My Notice',
    )
    return response


def launch_graphql_create_my_notice(title: str):
    response = retrieve_graphql(
        url=HttpConfig.graphql_url(),
        query="""
                mutation CREATE_MY_NOTICE($title: String!) {
                    createMyNotice(title: $title) {
                        myNotice {
                            id
                            title
                        }
                        success
                        errors
                    }
                }
            """,
        variables={
            "title": title
        },
        log_prefix='GraphQL Create My Notice',
    )
    return response


def test_get_my_notice_graphql_own_schema():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q, graphql_schema=my_graphql_schema)

    try:
        response = launch_graphql_get_my_notice('foo')
        assert response == {
            "data": {
                "getMyNotice": {
                    "success": True,
                    "errors": None,
                    "myNotice": {
                        "id": 'foo',
                        "title": 'my foo notice'
                    }
                }
            }
        }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)


def test_create_my_notice_graphql_own_schema():
    q = multiprocessing.Queue()
    server = http_server_start(response_queue=q, graphql_schema=my_graphql_schema)

    try:
        response = launch_graphql_create_my_notice('my foo notice')
        assert response == {
            "data": {
                "createMyNotice": {
                    "success": True,
                    "errors": None,
                    "myNotice": {
                        "id": 'foo',
                        "title": 'my foo notice'
                    }
                }
            }
        }
        assert queue_is_empty(q)
    finally:
        http_server_stop(server)
