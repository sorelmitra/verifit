def get_defaulted_prop(a_dict):
    def with_key(key):
        def with_default(default):
            return a_dict.get(key, default)
        return with_default
    return with_key


def get_prop(a_dict):
    def with_key(key):
        return get_defaulted_prop(a_dict)(key)(default=None)
    return with_key
