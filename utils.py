import re
from os import path
from datetime import datetime, timezone, tzinfo
from game import Game


def get_friendly_game_time(g: Game, now_utc: datetime = datetime.now(timezone.utc),
                           to_tz: tzinfo = timezone.utc):

    # Convert from UTC to provided tz
    game_local = g.datetime_utc.astimezone(to_tz)

    # Create friendly versions of time and tz
    friendly_time = game_local.strftime('%I:%M%p')
    friendly_time = re.sub('^0', '', friendly_time)  # Remove leading zero
    friendly_tz = game_local.strftime('%Z')

    # Measure difference in days based on provided 'now'
    days_delta = (g.datetime_utc - now_utc).days

    # Create friendly version of the day
    days = {0: 'Today', 1: 'Tomorrow'}
    days_default = game_local.strftime('%a, %b/%d')
    friendly_day = days.get(days_delta, days_default)

    return friendly_day, friendly_time, friendly_tz


class LogoProvider:
    def __init__(self, id_to_abbr: dict, logos_path: str):
        self.id_to_abbr = id_to_abbr
        self.logos_path = path.join(logos_path, 'logos')

    def get_team_logo_path(self, tid):
        abbr = self.id_to_abbr[tid].lower()
        ext = '.gif'
        b_path = path.join(self.logos_path, f'{abbr}-b{ext}')
        ry_path = path.join(self.logos_path, f'{abbr}-ry{ext}')
        return b_path, ry_path


class FontProvider:
    def __init__(self, fonts_path: str):
        self.fonts_path = path.join(fonts_path, 'fonts')

    def get_font_path_filename(self):
        return path.join(self.fonts_path, 'roboto', 'Roboto-Medium.ttf')
