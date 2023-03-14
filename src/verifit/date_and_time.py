def date_diff(a_date):
    def with_date(date_to_subtract):
        difference = a_date - date_to_subtract

        def apply(func=None):
            if func is None:
                return difference
            return func(difference)
        return apply
    return with_date


def in_minutes():
    def apply_to(difference):
        minutes = difference.seconds // 60
        if difference.days < 0:
            minutes = minutes + difference.days * 24 * 60

        def with_func(func=None):
            if func is None:
                return minutes
            return func(minutes)
        return with_func
    return apply_to
