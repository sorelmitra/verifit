import json
import requests
from python_graphql_client import GraphqlClient

from verifit.login import get_bearer_auth_base, get_bearer_authorization_header_value


QUERY = 'query'
VARIABLES = 'variables'
METHOD = 'method'
LOG_PREFIX = 'logPrefix'
PAYLOAD = 'payload'
AUTHORIZE = 'authorize'


def retrieveGraphQl(url):
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


def retrieveHttp(url):
    def with_config(config):
        method = config.get(METHOD, requests.get)
        prefix_message = config.get(LOG_PREFIX, f"Perform a {method} request")
        prefix = f"{prefix_message} to {url}"
        
        def getDefaultHeaders(options=None):
            headers = {
                'Content-Type': 'application/json'
            }
            if options.get(AUTHORIZE, False):
                headers['Authorization'] = get_bearer_authorization_header_value()
            print(prefix, 'headers', headers)
            return headers
        
        payload = config.get(PAYLOAD, None)
        print(prefix, 'payload', payload)
        headerOptions = { AUTHORIZE: config.get(AUTHORIZE, False) }
        response = method(
            url=url,
            data=None if payload is None else json.dumps(payload),
            headers=getDefaultHeaders(headerOptions),
        )
        print(prefix, 'response', response)
        data = response.json()
        print(prefix, 'JSON response', data)
        return data
    return with_config
