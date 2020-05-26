from datetime import date, timedelta


def default_event_date():
    """
    # :return: today if Wednesday, else next Wednesday
    # return next valid day
    """
    # today = date.today()
    # # Wednesday = 2
    # wednesday = today + timedelta((2 - today.weekday()) % 7)
    # return wednesday

    # Next valid day is 0, 1, 3, 4 (M, T, Th, F)
    today = date.today()
    if today.weekday() == 2:  # Wed push to Thu
        next_valid_day = today + timedelta(1)
    elif today.weekday() == 5:  # Sat push to Mon
        next_valid_day = today + timedelta(2)
    elif today.weekday() == 6:  # Sun push to Mon
        next_valid_day = today + timedelta(1)
    else:
        next_valid_day = today

    return next_valid_day


def school_year_start_date():
    """
    :return: September 1st of current school year
    """
    today = date.today()
    year = today.year
    if today.month < 9:
        year += 1

    return date(year, 9, 1)
