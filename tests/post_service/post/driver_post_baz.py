from verifit.config import get_store_reader
from verifit.retrieve import LOG_PREFIX, QUERY, VARIABLES, retrieve_graphql

get_env = get_store_reader()


def driver_post_baz(post_id):
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
          "id": post_id
      },
      LOG_PREFIX: 'Post via Post-Service-2',
    })
    data = response.get('data', None)
    assert data is not None
    post = data.get('post')
    assert post is not None
    return post
