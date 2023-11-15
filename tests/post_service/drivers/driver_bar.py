from verifit.config import get_env_reader
from verifit.retrieve import retrieve_graphql

get_env = get_env_reader()


def bar_post(*, userId, title, body):
    url = get_env('POST_SERVICE_2_URL')
    return retrieve_graphql(
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
            "id": userId,
            "title": title,
            "body": body
        },
        log_prefix='GraphQL Post'
    )


def bar_check_post_response(*, response, userId):
    assert response is not None
    data = response.get('data', None)
    assert data is not None
    post = data.get('post')
    assert post is not None
    assert post.get('id', None) == userId
    assert len(post.get('body', '')) > 0
