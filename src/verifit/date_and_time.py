def date_diff_in_minutes(a_date):
    def with_date(date_to_subtract):
        difference = a_date - date_to_subtract
        minutes = difference.seconds // 60
        if difference.days < 0:
            minutes = minutes + difference.days * 24 * 60
        return minutes
    return with_date
