def date_diff_in_minutes(date1, date2):
    difference = date1 - date2
    minutes = difference.seconds // 60
    if difference.days < 0:
        minutes = minutes + difference.days * 24 * 60
    return minutes
