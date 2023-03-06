import json

from .config import get_store_reader

filename = f".{get_store_reader()('ENV')}-cache.json"


def cache_read():
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def cache_write(cache):
    with open(filename, 'w') as f:
        json.dump(cache, f, indent=2)


def cache_set(key, value):
    cache = cache_read()
    cache[key] = value
    cache_write(cache)
    return value


def cache_get(key):
    cache = cache_read()
    return cache.get(key, None)


def retrieve_and_cache(retrieve_func):
    def with_arguments(args=None):
        def with_describer(describe_func):
            def with_key(key):
                resp = cache_get(key)
                if resp is None:
                    print(f"Cache miss key <{key}>")
                    if args is None:
                        retrieve_result = retrieve_func()
                    else:
                        retrieve_result = retrieve_func(args)
                    cache_set(key, retrieve_result)
                else:
                    print(f"Cache hit key <{key}>")
                resp = cache_get(key)
                print(f"{key}: {describe_func(resp)}")
                return resp
            return with_key
        return with_describer
    return with_arguments
