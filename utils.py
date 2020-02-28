import re


def get_friendly_local_date(g, days_ahead, to_tz=None):
    datetime_local = g.datetime_utc.astimezone(tz=to_tz)
    # Format time and then remove any leading 0 in the hour segment via RegEx if present
    time_local_str = datetime_local.strftime('%I:%M%p %Z')
    time_local_str = re.sub('^0', '', time_local_str)
    # Next few lines will get a readable string for when the game is, otherwise mm/dd
    days = {0: 'Today', 1: 'Tomorrow'}
    days_default = datetime_local.strftime('%a, %b/%d')
    day = days.get(days_ahead, days_default)
    return day, time_local_str
