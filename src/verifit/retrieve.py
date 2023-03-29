import json
import requests
from python_graphql_client import GraphqlClient

from verifit.login import get_bearer_auth_base


QUERY = 'query'
VARIABLES = 'variables'
METHOD = 'method'
LOG_PREFIX = 'logPrefix'
PAYLOAD = 'payload'


def retrieveGraphQl(url):
    def with_config(config):
        client = GraphqlClient(endpoint=url, auth=get_bearer_auth_base())
        prefix_message = config.get(LOG_PREFIX, 'Perform a POST request')
        prefix = f"{prefix_message} to {url}"
        print(prefix, 'variables', config[VARIABLES])
        response = client.execute(config[QUERY], config[VARIABLES])
        print(prefix, 'response', response)
        return response
    return with_config


def retrieveHttp(url):
    def with_config(config):
        method = config.get(METHOD, requests.get)
        prefix_message = config.get(LOG_PREFIX, f"Perform a {method} request")
        prefix = f"{prefix_message} to {url}"
        payload = config.get(PAYLOAD, None)
        print(prefix, 'payload', payload)
        response = method(
            url=url,
            data=None if payload is None else json.dumps(payload),
            headers={
                'Content-Type': 'application/json'
            },
        )
        print(prefix, 'response', response)
        data = response.json()
        print(prefix, 'JSON response', data)
        return data
    return with_config
