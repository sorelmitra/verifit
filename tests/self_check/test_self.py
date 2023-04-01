import pytest
from verifit.cache import ARG, KEY, DESCRIBE_FUNC, cache_get, cache_set, retrieve_and_cache
from verifit.config import get_store_reader, get_store_writer
from verifit.driver import select_driver
from verifit.login import ACCESS_TOKEN, LOGIN_DATA
from verifit.retrieve import EXTRA_HEADERS, USE_DEFAULT_HEADERS, retrieve_http, METHOD, AUTHORIZE

get_env = get_store_reader()
set_env = get_store_writer()


def test_cache():
    DUMMY = 'dummy'
    called = False

    def dummy_func(arg):
        nonlocal called
        called = True
        return f"{arg} func"

    retrieve_dummy = retrieve_and_cache(config={
        KEY: DUMMY,
        ARG: 'dummy',
        DESCRIBE_FUNC: lambda dummy_data : f"I'm describing {dummy_data}",
    })

    cache_set(DUMMY)(None)
    assert cache_get(DUMMY) is None
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
    set_env(LOGIN_DATA)({ACCESS_TOKEN: 'x'})
    stub = mocker.stub(name='method')
    retrieve_http('url')({
        METHOD: stub,
        AUTHORIZE: True,
    })
    stub.assert_called_once_with(url='url', data=None, headers=expected_headers)


def test_retrieve_extra_headers(mocker):
    expected_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer x',
        'X1': 'x',
        'X2': 'y'
    }
    set_env(LOGIN_DATA)({ACCESS_TOKEN: 'x'})
    stub = mocker.stub(name='method')
    retrieve_http('url')({
        METHOD: stub,
        AUTHORIZE: True,
        EXTRA_HEADERS: {
            'X1': 'x',
            'X2': 'y'
        }
    })
    stub.assert_called_once_with(url='url', data=None, headers=expected_headers)


def test_retrieve_custom_headers(mocker):
    expected_headers = {
        'X1': 'x',
        'X2': 'y'
    }
    set_env(LOGIN_DATA)({ACCESS_TOKEN: 'x'})
    stub = mocker.stub(name='method')
    retrieve_http('url')({
        METHOD: stub,
        AUTHORIZE: True,
        USE_DEFAULT_HEADERS: False,
        EXTRA_HEADERS: {
            'X1': 'x',
            'X2': 'y'
        }
    })
    stub.assert_called_once_with(url='url', data=None, headers=expected_headers)


def test_driver_names():
    def driver_stuff_foo():
        pass
    
    def driver_stuff_bar():
        pass
    
    def driver_stuff_baz():
        pass
    
    def driver_stuff_foo_bar():
        pass 
    
    drivers = [driver_stuff_foo, driver_stuff_bar, driver_stuff_baz]
    
    assert select_driver('foo')(drivers) == driver_stuff_foo
    assert select_driver('bar')(drivers) == driver_stuff_bar
    with pytest.raises(Exception, match='Could not find driver'):
        select_driver('bartender')(drivers)

    drivers.extend([driver_stuff_foo_bar])
    with pytest.raises(Exception, match='More than one driver'):
        select_driver('bar')(drivers)
