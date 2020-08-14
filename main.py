#!/usr/bin/python
# -*- coding:utf-8 -*-
import config
# noinspection PyUnresolvedReferences
from datetime import datetime, timedelta
from display import get_display
from utils import LogoProvider, FontProvider
from ui import get_ui_builder, GameStatus
from time import sleep
import os
import pytz
from net import NhlApi, DebugNhlApi, NoUpcomingGameError

curr_dir = os.path.dirname(os.path.realpath(__file__))

if config.DEBUG_ENABLED is True:
    debugGame = os.path.join(curr_dir, config.DEBUG_GAME)
    debugDetails = os.path.join(curr_dir, config.DEBUG_GAME_DETAILS) if config.DEBUG_GAME_DETAILS is not None else None
    api = DebugNhlApi(debugGame, debugDetails)
else:
    api = NhlApi(config.CHECK_LIMIT_DAYS)

res_path = os.path.join(curr_dir, 'res')
fp = FontProvider(res_path)
lp = LogoProvider(api.abbrs, res_path)

fav_team_id = api.get_team_id(config.FAVORITE_TEAM)
game_date = datetime.today().astimezone(tz=pytz.timezone(config.TIMEZONE))

# Loop if the game is live
while True:

    game = None
    try:
        game = api.get_next_game(fav_team_id, game_date)  # -/+ timedelta(days=1)
    except NoUpcomingGameError:
        print('No upcoming game was found')

    is_live = game is not None \
        and (GameStatus.LIVE == game.status
             or GameStatus.LIVE_CRITICAL == game.status)

    d = get_display()
    d.start()
    d.clear()

    try:
        get_ui_builder(d, fp, lp, game) \
            .deploy()
    finally:
        d.stop()

    if is_live is True:
        sleep(config.CHECK_UPDATE_LIVE_GAME_SECONDS)
    else:
        break
