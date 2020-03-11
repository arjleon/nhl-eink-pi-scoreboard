#!/usr/bin/python
# -*- coding:utf-8 -*-
import constants
from datetime import datetime, timedelta
import json
import requests
from game import Game, GameStatus, GameDetails
from display import get_display
from utils import LogoProvider, FontProvider
from ui import get_ui_builder
import os
from time import sleep
import pytz


def write_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)


def read_file(filename):
    with open(filename, 'r') as file:
        return file.read()


def get_url(endpoint, *args):
    all_args = ''
    for arg in args:
        all_args += f'&{arg}'
    return f'{constants.API_BASE}{endpoint}?{all_args}'


def get_teams():
    filename = constants.FILE_TEAMS + '.json'

    for f in [f'../{filename}', filename]:
        if os.path.exists(f):
            print(f'Teams data exists in {f}')
            return json.loads(read_file(f))

    if os.path.exists(filename):
        print('Teams data exists')
        return json.loads(read_file(filename))

    print('Fetching teams data')
    response = requests.get(get_url(constants.API_TEAMS))
    if response:
        text = response.text
        write_file(filename, text)
        return json.loads(text)
    else:
        raise Exception('No teams data available')


def get_abbreviations(data):
    if data:
        teams = data['teams']
        count = len(teams)
        if count > 0:
            abbr = {}
            for team in teams:
                abbr[team['id']] = team['abbreviation']
            return abbr


def get_team_id(abbr):
    for key in id_to_abbr.keys():
        if id_to_abbr[key] == abbr:
            return key
    raise Exception('Team abbreviation is incorrect')


def get_game_details(link: str):
    response = requests.get(get_url(link), timeout=(60, 60))
    return GameDetails(json.loads(response.content))


def get_next_game(tid, date_time=datetime.today(), loop=0):
    while loop < constants.NEXT_GAME_CHECK_LIMIT:
        team_arg = f'teamId={tid}'
        date_arg = f'date={date_time.strftime(constants.API_DATE_FORMAT)}'

        response = requests.get(get_url(constants.API_SCHEDULE, team_arg, date_arg), timeout=(60, 60))
        data = json.loads(response.content)

        # f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tests/tests.games.live.json'))
        # data = json.loads(f.read())
        # f.close()

        count = data['totalGames']
        if count > 0:
            single_game = Game(data['dates'][0]['games'][0])
            return single_game
        else:
            pause = 1
            print(f'({loop}) No games, checking next day in {pause}s...')
            sleep(pause)
            return get_next_game(tid, date_time + timedelta(days=1), loop + 1)
    raise Exception(f'({loop}) Error, could not find the next match')


team_data = get_teams()
id_to_abbr = get_abbreviations(team_data)
res_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'res')
fp = FontProvider(res_path)
lp = LogoProvider(id_to_abbr, res_path)
team_id = get_team_id(constants.FAVORITE_TEAM)
# -/+ timedelta(days=1)
game = get_next_game(team_id, datetime.today().astimezone(tz=pytz.timezone(constants.TIMEZONE)))

if GameStatus.LIVE == game.status \
        or GameStatus.LIVE_CRITICAL == game.status \
        or GameStatus.FINAL == game.status:

    details = get_game_details(game.link)
    # j = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tests/tests.game.period1.pp.json'))
    # details = GameDetails(json.loads(j.read()))
    # j.close()
    game.attach_details(details)

d = get_display()
d.start()
d.clear()

try:
    get_ui_builder(d, fp, lp, game)\
        .deploy()
finally:
    d.stop()
