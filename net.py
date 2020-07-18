import json
import requests
import os
from utils import write_file, read_file
from game import Game, GameStatus, GameDetails
from datetime import datetime, timedelta
from time import sleep

API_BASE_URL = 'http://statsapi.web.nhl.com'
API_SCHEDULE = 'api/v1/schedule'
API_TEAMS = 'api/v1/teams'
API_DATE_FORMAT = '%Y-%m-%d'


class NhlApi:

    def __init__(self, check_days_limit: int = 10):
        self.timeouts = (60, 60)
        self.check_limit = check_days_limit
        teams = NhlApi.get_teams_data(self)
        self.abbrs = self.__get_teams_abbreviations(teams)

    @staticmethod
    def build_url(endpoint, *args) -> str:
        all_args = ''
        for arg in args:
            all_args += f'&{arg}'
        if len(all_args) > 0 and all_args[0] == '&':
            all_args = all_args[1:]
        return f'{API_BASE_URL}/{endpoint}?{all_args}'

    def get_teams_data(self):

        # Check for existing local data
        filename = 'teams.json'

        for f in [f'../{filename}', filename]:
            if os.path.exists(f):
                print(f'Teams data exists in {f}')
                return json.loads(read_file(f))

        print('Fetching teams data')
        url = NhlApi.build_url(API_TEAMS)
        res = self.get(url)
        if res:
            text = res.text
            write_file(filename, text)
            return json.loads(text)
        else:
            raise Exception('No teams data available')

    def get(self, url):
        return requests.get(url, timeout=self.timeouts)

    @staticmethod
    def __get_teams_abbreviations(teams_data):
        teams = teams_data['teams']
        if len(teams) > 0:
            abbr = {}
            for team in teams:
                abbr[team['id']] = team['abbreviation']
            return abbr

    def get_team_id(self, abbr):
        for key in self.abbrs.keys():
            if self.abbrs[key] == abbr:
                return key
        raise Exception('Team abbreviation is incorrect')

    def __get_game_details(self, link: str) -> GameDetails:
        res = self.get(NhlApi.build_url(link))
        return GameDetails(json.loads(res.content))

    def get_next_game(self, tid, date_time=datetime.today(), loop=0):
        while loop < self.check_limit:
            team_arg = f'teamId={tid}'
            date_arg = f'date={date_time.strftime(API_DATE_FORMAT)}'

            url = NhlApi.build_url(API_SCHEDULE, team_arg, date_arg)
            res = self.get(url)
            data = json.loads(res.content)

            count = data['totalGames']
            if count > 0:

                game = Game(data['dates'][0]['games'][0])

                if GameStatus.LIVE == game.status \
                        or GameStatus.LIVE_CRITICAL == game.status \
                        or GameStatus.FINAL == game.status:

                    details = self.__get_game_details(game.link)
                    game.attach_details(details)
                return game
            else:
                seconds = 1
                print(f'No games, checking next day in {seconds}s... ({loop})')
                sleep(seconds)
                return self.get_next_game(tid, date_time + timedelta(days=1), loop + 1)
        raise Exception(f'({loop}) Error, could not find the next match')


class DebugNhlApi(NhlApi):

    def __init__(self, local_game_data, local_game_data_details=None):
        super().__init__()
        if local_game_data is None:
            raise ValueError(local_game_data)
        self.game = local_game_data
        self.details = local_game_data_details

    def get_next_game(self, tid, date_time=datetime.today(), loop=0):

        g = open(self.game)
        data = json.loads(g.read())
        g.close()
        game = Game(data['dates'][0]['games'][0])

        if self.details is not None:
            d = open(self.details)
            details = GameDetails(json.loads(d.read()))
            d.close()
            game.attach_details(details)

        return game
