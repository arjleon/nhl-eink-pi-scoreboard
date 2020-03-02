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


class DetailedGameState:
    def __init__(self, j):
        linescore = j['liveData']['linescore']
        self.period = linescore['currentPeriodOrdinal']
        self.period_remaining = linescore['currentPeriodTimeRemaining']
        self.strength = linescore['powerPlayStrength']
        pp_info = linescore['powerPlayInfo']
        self.in_pp = bool(pp_info['inSituation'])
        self.pp_remaining_seconds = pp_info['situationTimeRemaining']
        teams_info = linescore['teams']
        self.home = DetailedGameStateTeam(teams_info['home'])
        self.away = DetailedGameStateTeam(teams_info['away'])
        intermission_info = linescore['intermissionInfo']
        self.in_intermission = intermission_info['inIntermission']
        self.intermission_remaining_seconds = intermission_info['intermissionTimeRemaining']


class DetailedGameStateTeam:
    def __init__(self, j):
        self.goalie_pulled = bool(j['goaliePulled'])
        self.num_skaters = j['numSkaters']
        self.in_pp = bool(j['powerPlay'])
