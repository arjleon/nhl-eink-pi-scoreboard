#!/usr/bin/python
# -*- coding:utf-8 -*-
import constants
from datetime import datetime, timedelta
import json
import requests
import os
from time import sleep
from game import Game, GameStatus
from display import Display
from utils import TeamIconProvider, FontProvider
from DisplayCanvas import UpcomingGameCanvas


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
    if os.path.exists(filename):
        print('Teams data exists')
        return json.loads(read_file(filename))
    else:
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


def get_next_game(tid, date_time=datetime.today(), loop=0):
    while loop < constants.NEXT_GAME_CHECK_LIMIT:
        team_arg = f'teamId={tid}'
        date_arg = f'date={date_time.strftime(constants.API_DATE_FORMAT)}'
        response = requests.get(get_url(constants.API_SCHEDULE, team_arg, date_arg), timeout=60)
        data = json.loads(response.content)
        count = data['totalGames']
        if count > 0:
            single_game = Game(data['dates'][0]['games'][0])
            return single_game, loop
        else:
            pause = 1
            print(f'({loop}) No games, checking next day in {pause}s...')
            sleep(pause)
            return get_next_game(tid, date_time + timedelta(days=1), loop + 1)
    raise Exception(f'({loop}) Error, could not find the next match')


# def print_game_info(g, daysahead):
#
#     day, time = utils.get_friendly_local_date(g, daysahead)
#     expanded_status = f'{day} {time}'
#
#     if g.status == GameStatus.FINAL:
#         expanded_status = 'Final: %d - %d' % (g.away.score, g.home.score)
#         display.show_finished_game(g, 'edm', 'vgk')
#
#     home_record = '%d-%d-%d' % (g.home.wins, g.home.losses, g.home.ot)
#     away_record = '%d-%d-%d' % (g.away.wins, g.away.losses, g.away.ot)
#     print(f'({away_record}) {id_to_abbr[g.away.id]} @ {id_to_abbr[g.home.id]} ({home_record})\n{expanded_status}')

id_to_abbr = get_abbreviations(get_teams())
resources_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'res')
font_provider = FontProvider(resources_path)
icon_provider = TeamIconProvider(id_to_abbr, resources_path)
team_id = get_team_id('VGK')
game, days_delta = get_next_game(team_id, datetime.today())  # - timedelta(days=1)

display = Display()
display.start()
display.clear()

try:
    canvas = UpcomingGameCanvas(display, font_provider, game, icon_provider, days_delta)
finally:
    display.stop()
