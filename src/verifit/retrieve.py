import json
import requests
from python_graphql_client import GraphqlClient

from .login import get_bearer_auth_base, get_bearer_authorization_header_value


QUERY = 'query'
VARIABLES = 'variables'
METHOD = 'method'
LOG_PREFIX = 'logPrefix'
PAYLOAD = 'payload'
AUTHORIZE = 'authorize'
EXTRA_HEADERS = 'extraHeaders'
USE_DEFAULT_HEADERS = 'useDefaultHeaders'


def retrieve_graphql(url):
    def with_config(config):
        use_auth = config.get(AUTHORIZE, False)
        auth = get_bearer_auth_base() if use_auth else None
        client = GraphqlClient(endpoint=url, auth=auth)
        prefix_message = config.get(LOG_PREFIX, 'Perform a POST request')
        prefix = f"{prefix_message} to {url}"
        print(prefix, 'variables', config[VARIABLES])
        response = client.execute(config[QUERY], config[VARIABLES])
        print(prefix, 'response', response)
        return response
    return with_config


def retrieve_http(url):
    def with_config(config):
        method = config.get(METHOD, requests.get)
        prefix_message = config.get(LOG_PREFIX, f"Perform a {method.__name__} request")
        prefix = f"{prefix_message} to {url}"

        def get_default_headers():
            headers = {}
            if config.get(USE_DEFAULT_HEADERS, True):
                headers.update({
                    'Content-Type': 'application/json'
                })
                if config.get(AUTHORIZE, False):
                    headers['Authorization'] = get_bearer_authorization_header_value()
            headers.update(config.get(EXTRA_HEADERS, {}))
            print(prefix, 'headers', headers)
            return headers

        payload = config.get(PAYLOAD, None)
        print(prefix, 'payload', payload)
        response = method(
            url=url,
            data=None if payload is None else json.dumps(payload),
            headers=get_default_headers(),
        )
        print(prefix, 'response', response)
        data = response.json()
        print(prefix, 'JSON response', data)
        return data
    return with_config
