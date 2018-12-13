from datetime import date, timedelta


def default_event_date():
    """
    :return: today if Wednesday, else next Wednesday
    """
    today = date.today()
    # Wednesday = 2
    wednesday = today + timedelta((2 - today.weekday()) % 7)
    return wednesday


def school_year_start_date():
    """
    :return: September 1st of current school year
    """
    today = date.today()
    year = today.year
    if today.month < 9:
        year += 1

    return date(year, 9, 1)
