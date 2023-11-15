from verifit.cache import cache_get, cache_set, retrieve_and_cache
from verifit.config import get_env_reader
from verifit.login import ACCESS_TOKEN
from verifit.retrieve import retrieve_http

get_env = get_env_reader()


def test_cache():
    dummy = 'dummy'
    called = False

    def dummy_func(arg):
        nonlocal called
        called = True
        return f"{arg} func"

    retrieve_dummy = retrieve_and_cache(key=dummy, arg=dummy,
                                        describe_func=lambda dummy_data : f"I'm describing {dummy_data}")

    cache_set(dummy)(None)
    assert cache_get(dummy) is None
    value = retrieve_dummy(func=dummy_func)
    assert value == 'dummy func'
    assert called

    called = False
    value = retrieve_dummy(func=dummy_func)
    assert value == 'dummy func'
    assert not called


def test_retrieve_default_headers(mocker):
    expected_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer x',
    }
    stub = mocker.stub(name='method')
    retrieve_http(url='url', method=stub, auth='Bearer x')
    stub.assert_called_once_with(url='url', data=None, headers=expected_headers)


def test_retrieve_extra_headers(mocker):
    expected_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer x',
        'X1': 'x',
        'X2': 'y'
    }
    stub = mocker.stub(name='method')
    retrieve_http(url='url', method=stub, auth='Bearer x',
                  extra_headers={
                      'X1': 'x',
                      'X2': 'y'
                  })
    stub.assert_called_once_with(url='url', data=None, headers=expected_headers)


def test_retrieve_custom_headers(mocker):
    expected_headers = {
        'X1': 'x',
        'X2': 'y'
    }
    stub = mocker.stub(name='method')
    retrieve_http(url='url', method=stub, auth='Bearer x', use_default_headers=False,
                  extra_headers={
                      'X1': 'x',
                      'X2': 'y'
                  })
    stub.assert_called_once_with(url='url', data=None, headers=expected_headers)


