import requests

from verifit.config import get_env_reader
from verifit.login import ACCESS_TOKEN, EXPIRY_DATE
from verifit.retrieve import retrieve_graphql, retrieve_http

get_env = get_env_reader()


def get_bearer_auth_base(access_token):
    class BearerAuth(requests.auth.AuthBase):
        def __init__(self, token):
            self.token = token

        def __call__(self, r):
            r.headers["authorization"] = "Bearer " + self.token
            return r

    return BearerAuth(access_token)


def test_post_graphql():
    url = get_env('POST_SERVICE_2_URL')
    response = retrieve_graphql(
        url=url,
        query="""
            query GET_POST($id: ID!) {
                post(id: $id) {
                    id
                    title
                    body
                }
            }
        """,
        variables={
            "id": '1'
        },
        log_prefix='GraphQL Post',
        auth=get_bearer_auth_base('dummy token')  # This is how you authorize a GraphQL request
    )
    data = response.get('data', None)
    assert data is not None
    post = data.get('post')
    assert post is not None
    assert post.get('id', None) == '1'
    assert len(post.get('body', '')) > 0


def test_post_rest_api():
    url = f"{get_env('POST_SERVICE_1_URL')}/posts"
    payload = {
        "userId": '2',
        "title": "test post",
        "body": "test post body"
    }
    data = retrieve_http(url=url, method=requests.post, log_prefix='REST API Post', payload=payload)
    assert data is not None
    assert data.get('userId') == '2'
    assert len(data.get('title', '')) > 0
    assert len(data.get('body', '')) > 0
