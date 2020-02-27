import enum
from datetime import datetime


class Game:
    def __init__(self, j):
        self.id = j['gamePk']
        self.datetime_utc = datetime.fromisoformat(j['gameDate'].replace('Z', '+00:00'))
        self.status = GameStatus(int(j['status']['statusCode']))
        self.link = j['link']
        j_teams = j['teams']
        self.home = Team(j_teams['home'])
        self.away = Team(j_teams['away'])

        try:
            self.is_time_tbd = bool(j['startTimeTBD'])
        except KeyError:
            self.is_time_tbd = False


class GameStatus(enum.Enum):
    SCHEDULED = 1
    LIVE = 3
    LIVE_CRITICAL = 4
    FINAL = 7


class Team:
    def __init__(self, j):
        self.score = j['score']
        meta = j['team']
        self.id = meta['id']
        self.name = meta['name']
        record = j['leagueRecord']
        self.wins = record['wins']
        self.losses = record['losses']
        self.ot = record['ot']
