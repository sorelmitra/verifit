from python_graphql_client import GraphqlClient

from verifit.config import get_store_reader

get_env = get_store_reader()


def execute(post_id):
    client = GraphqlClient(endpoint=get_env('POST_SERVICE_2_URL'))
    query = """
        query GET_POST($id: ID!) {
          post(id: $id) {
            id
            title
            body
          }
        }
    """
    variables = {
      "id": post_id
    }
    print('Posting via Post-Service-2', variables)
    response = client.execute(query, variables)
    print('Received GraphQL post response', response)
    data = response.get('data', None)
    assert data is not None
    post = data.get('post')
    assert post is not None
    return post
