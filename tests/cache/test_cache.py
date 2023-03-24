from verifit.cache import ARG, KEY, DESCRIBE_FUNC, cache_get, cache_set, retrieve_and_cache


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
