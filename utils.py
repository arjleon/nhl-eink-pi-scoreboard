import re
from os import path
from datetime import datetime, timezone, tzinfo, timedelta
from game import Game


def write_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)


def read_file(filename):
    with open(filename, 'r') as file:
        return file.read()


def get_friendly_game_time(g: Game, now_utc: datetime = datetime.now(timezone.utc),
                           to_tz: tzinfo = timezone.utc):

    # Convert from UTC to provided tz
    game_local = g.datetime_utc.astimezone(to_tz)
    now_local = now_utc.astimezone(to_tz)

    # Create friendly versions of time and tz
    friendly_time = game_local.strftime('%I:%M%p')
    friendly_time = re.sub('^0', '', friendly_time)  # Remove leading zero
    friendly_tz = game_local.strftime('%Z')

    # Measure difference in days based on provided 'now'
    normalized_game_local = datetime(game_local.year, game_local.month, game_local.day)
    normalized_now_local = datetime(now_local.year, now_local.month, now_local.day)
    days_delta = (normalized_game_local - normalized_now_local).days

    # Create friendly version of the day
    days = {0: 'Today', 1: 'Tomorrow'}
    days_default = game_local.strftime('%a, %b/%d')
    friendly_day = days.get(days_delta, days_default)

    return friendly_day, friendly_time, friendly_tz


def pp_seconds_to_friendly(seconds: int):
    d = timedelta(seconds=seconds)
    formatted = str(d)
    return formatted[formatted.index(':') + 2:]


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
