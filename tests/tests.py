import unittest
import main
import json
from game import Game, GameStatus
import utils
import pytz
from datetime import timedelta


class MyTestCase(unittest.TestCase):
    def test_url_endpoint(self):
        url = main.get_url('test')
        self.assertIsNotNone(url)
        self.assertTrue(url.endswith('/test?'))

    def test_url_endpoint_1arg(self):
        url = main.get_url('test', 'k1=v1')
        self.assertTrue(url.endswith('/test?&k1=v1'))

    def test_url_endpoint_2arg(self):
        url = main.get_url('test', 'k1=v1', 'a=b')
        self.assertTrue(url.endswith('/test?&k1=v1&a=b'))

    def test_json_parsing(self):
        g = get_game_from_file('tests.games.live.json')
        # Game data
        self.assertEqual(g.id, 2019020794)
        self.assertEqual(g.link, '/api/v1/game/2019020794/feed/live')
        self.assertEqual(g.status, GameStatus.LIVE)
        self.assertFalse(g.is_time_tbd)
        # Away data
        self.assertEqual('Florida Panthers', g.away.name)
        self.assertEqual(13, g.away.id)
        self.assertEqual(28, g.away.wins)
        self.assertEqual(16, g.away.losses)
        self.assertEqual(5, g.away.ot)
        self.assertEqual(0, g.away.score)
        # Home data
        self.assertEqual(8, g.home.id)
        self.assertEqual('Montréal Canadiens', g.home.name)
        self.assertEqual(23, g.home.wins)
        self.assertEqual(22, g.home.losses)
        self.assertEqual(7, g.home.ot)
        self.assertEqual(2, g.home.score)

    def test_json_scheduled_game(self):
        g = get_game_from_file('tests.games.scheduled.json')
        self.assertEqual(g.status, GameStatus.SCHEDULED)
        self.assertFalse(g.is_time_tbd)

    def test_json_live_game(self):
        g = get_game_from_file('tests.games.live.json')
        self.assertEqual(g.status, GameStatus.LIVE)
        self.assertFalse(g.is_time_tbd)

    def test_json_livecritical_game(self):
        g = get_game_from_file('tests.games.livecritical.json')
        self.assertEqual(g.status, GameStatus.LIVE_CRITICAL)
        self.assertFalse(g.is_time_tbd)

    def test_json_final_game(self):
        g = get_game_from_file('tests.games.final.json')
        self.assertEqual(g.status, GameStatus.FINAL)
        self.assertFalse(g.is_time_tbd)

    def test_friendly_today_utc(self):
        g = get_game_from_file('tests.games.scheduled.json')
        now_utc = g.datetime_utc - timedelta(hours=23)  # Diff of less than a day
        day, time, tz = utils.get_friendly_game_time(g, now_utc)

        self.assertEqual('Today', day)
        self.assertEqual('12:00AM', time)   # As defined in the input test file
        self.assertEqual('UTC', tz)         # As no tz was provided

    def test_friendly_tomorrow_us_pacific(self):
        g = get_game_from_file('tests.games.scheduled.json')
        now_utc = g.datetime_utc - timedelta(days=1, hours=20)  # Diff over 1 day, less than 2
        day, time, tz = utils.get_friendly_game_time(g, now_utc, pytz.timezone('US/Pacific'))

        self.assertEqual('Tomorrow', day)
        self.assertEqual('4:00PM', time)    # As defined in the input test file
        self.assertEqual('PST', tz)         # As no tz was provided

    def test_friendly_mmdd_us_eastern(self):
        g = get_game_from_file('tests.games.scheduled.json')
        now_utc = g.datetime_utc - timedelta(days=5)  # Diff over 2 day
        day, time, tz = utils.get_friendly_game_time(g, now_utc, pytz.timezone('US/Eastern'))

        self.assertEqual('Sat, Feb/01', day)
        self.assertEqual('7:00PM', time)    # As defined in the input test file
        self.assertEqual('EST', tz)         # As no tz was provided


def get_game_from_file(filename):
    f = open(filename, 'r')
    j = json.loads(f.read())
    f.close()
    return Game(j['dates'][0]['games'][0])


if __name__ == '__main__':
    unittest.main()
