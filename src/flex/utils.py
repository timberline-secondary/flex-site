from datetime import date, timedelta


def default_event_date():
    """
    :return: today if Wednesday, else next Wednesday
    """
    today = date.today()
    # Wednesday = 2
    wednesday = today + timedelta((2 - today.weekday()) % 7)
    return wednesday
