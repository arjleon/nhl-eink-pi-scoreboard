import enum
from datetime import datetime


class GameStatus(enum.Enum):
    UNEXPECTED = -1
    SCHEDULED = 1
    SCHEDULED_TIMETBD = 8
    LIVE = 3
    LIVE_CRITICAL = 4
    FINAL = 6


class Team:
    def __init__(self, j):
        self.score = j['score']
        meta = j['team']
        self.id = meta['id']
        self.name = meta['name']
        record = j['leagueRecord']
        self.wins = record['wins']
        self.losses = record['losses']

        # Playoffs have no OT record

        try:
            self.ot = record['ot']
        except KeyError:
            self.ot = None


class GameDetailsTeam:
    def __init__(self, j):
        self.goalie_pulled = bool(j['goaliePulled'])
        self.num_skaters = j['numSkaters']
        self.in_pp = bool(j['powerPlay'])


class GameDetails:
    def __init__(self, j):
        linescore = j['liveData']['linescore']
        self.period = linescore['currentPeriod']
        self.period_ordinal = linescore['currentPeriodOrdinal']
        self.period_remaining = linescore['currentPeriodTimeRemaining']
        self.strength = linescore['powerPlayStrength']
        pp_info = linescore['powerPlayInfo']
        self.in_pp = bool(pp_info['inSituation'])
        self.pp_remaining_seconds = pp_info['situationTimeRemaining']
        teams_info = linescore['teams']
        self.home = GameDetailsTeam(teams_info['home'])
        self.away = GameDetailsTeam(teams_info['away'])
        intermission_info = linescore['intermissionInfo']
        self.in_intermission = intermission_info['inIntermission']
        self.intermission_remaining_seconds = intermission_info['intermissionTimeRemaining']


class Game:
    def __init__(self, j):
        self.id = j['gamePk']
        self.datetime_utc = datetime.fromisoformat(j['gameDate'].replace('Z', '+00:00'))
        status_code = int(j['status']['statusCode'])
        self.original_status = status_code
        try:
            self.status = GameStatus(status_code)
        except ValueError:
            self.status = GameStatus.UNEXPECTED

        self.link = j['link']
        j_teams = j['teams']
        self.home = Team(j_teams['home'])
        self.away = Team(j_teams['away'])
        self.details = None

        try:
            self.is_time_tbd = bool(j['startTimeTBD'])
        except KeyError:
            self.is_time_tbd = False

    def attach_details(self, d: GameDetails):
        self.details = d

    def has_details(self):
        return self.details is not None
