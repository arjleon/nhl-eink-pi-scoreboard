#!/usr/bin/python
# -*- coding:utf-8 -*-
import config
# noinspection PyUnresolvedReferences
from datetime import datetime, timedelta
from display import get_display
from utils import LogoProvider, FontProvider
from ui import get_ui_builder
import os
import pytz
from net import NhlApi, DebugNhlApi

curr_dir = os.path.dirname(os.path.realpath(__file__))

if config.DEBUG_GAME is not None and config.DEBUG_GAME_DETAILS is not None:
    api = DebugNhlApi(os.path.join(curr_dir, config.DEBUG_GAME),
                      os.path.join(curr_dir, config.DEBUG_GAME_DETAILS))
else:
    api = NhlApi()

res_path = os.path.join(curr_dir, 'res')
fp = FontProvider(res_path)
lp = LogoProvider(api.abbrs, res_path)

fav_team_id = api.get_team_id(config.FAVORITE_TEAM)
game_date = datetime.today().astimezone(tz=pytz.timezone(config.TIMEZONE))
game = api.get_next_game(fav_team_id, game_date)  # -/+ timedelta(days=1)

d = get_display()
d.start()
d.clear()

try:
    get_ui_builder(d, fp, lp, game)\
        .deploy()
finally:
    d.stop()
