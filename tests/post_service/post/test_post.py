from datetime import datetime
import requests

from verifit.config import get_store_writer, get_store_reader
from verifit.login import ACCESS_TOKEN, EXPIRY_DATE, LOGIN_DATA
from verifit.prop import get_prop, get_defaulted_prop
from verifit.retrieve import retrieve_graphql, QUERY, VARIABLES, LOG_PREFIX, retrieve_http, METHOD, PAYLOAD, AUTHORIZE

get_env = get_store_reader()
set_env = get_store_writer()


def simulate_login():
    # We're simulating login because our test GraphQL server doesn't have
    # login, and we want to showcase using our auth helper for GraphQL
    set_env(LOGIN_DATA)({
        ACCESS_TOKEN: 'dummy token',
        EXPIRY_DATE: datetime.now()
    })


def test_post_graphql():
    simulate_login()
    url = get_env('POST_SERVICE_2_URL')
    response = retrieve_graphql(url)({
        QUERY: """
            query GET_POST($id: ID!) {
                post(id: $id) {
                    id
                    title
                    body
                }
            }
        """,
        VARIABLES: {
            "id": '1'
        },
        LOG_PREFIX: 'GraphQL Post',
        AUTHORIZE: True,
    })
    data = response.get('data', None)
    assert data is not None
    post = data.get('post')
    assert post is not None
    assert post.get('id', None) == '1'
    assert len(get_defaulted_prop(post)('body')('')) > 0


def test_post_rest_api():
    url = f"{get_env('POST_SERVICE_1_URL')}/posts"
    payload = {
        "userId": '2',
        "title": "test post",
        "body": "test post body"
    }
    data = retrieve_http(url)({
        METHOD: requests.post,
        LOG_PREFIX: 'REST API Post',
        PAYLOAD: payload,
    })
    assert data is not None
    assert get_prop(data)('userId') == '2'
    assert len(get_defaulted_prop(data)('title')('')) > 0
    assert len(get_defaulted_prop(data)('body')('')) > 0
