import re
from os import path


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


class TeamIconProvider:
    def __init__(self, id_to_abbr: dict, icons_path: str):
        self.id_to_abbr = id_to_abbr
        self.icons_path = path.join(icons_path, 'logos')

    def get_team_icon_path(self, tid):
        abbr = self.id_to_abbr[tid].lower()
        ext = '.gif'
        b_path = path.join(self.icons_path, f'{abbr}-b{ext}')
        ry_path = path.join(self.icons_path, f'{abbr}-ry{ext}')
        return b_path, ry_path


class FontProvider:
    def __init__(self, fonts_path: str):
        self.fonts_path = path.join(fonts_path, 'fonts')

    def get_font_path_filename(self):
        return path.join(self.fonts_path, 'roboto', 'Roboto-Medium.ttf')
