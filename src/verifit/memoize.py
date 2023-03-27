from verifit.prop import get_prop


def create_memoizer(func):
    func_result_cache = {}

    def memoize(arg=None):
        cached_value = get_prop(func_result_cache)(arg)
        if cached_value is None:
            if arg is None:
                func_result_cache[arg] = func()
            else:
                func_result_cache[arg] = func(arg)
        return func_result_cache.get(arg)

    return memoize
