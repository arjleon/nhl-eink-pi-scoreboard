from display import *
from layout import *
from utils import *
from game import *
import pytz
import config
import utils


def get_ui_builder(d: BaseDisplay, fp: FontProvider, lp: LogoProvider, g: Game):

    if g is None:
        return NoGame(d, fp)

    elif GameStatus.FINAL == g.status or GameStatus.FINAL_ALT == g.status:
        return FinalGame(d, g, fp, lp)

    elif GameStatus.LIVE == g.status or GameStatus.LIVE_CRITICAL == g.status:
        return LiveGame(d, g, fp, lp)

    elif GameStatus.SCHEDULED == g.status:
        return ScheduledGame(d, g, fp, lp)

    elif GameStatus.SCHEDULED_TIMETBD == g.status:
        return ScheduledTimeTbdGame(d, g, fp, lp)

    elif GameStatus.POSTPONED == g.status:
        return PostponedGame(d, g, fp, lp)

    else:
        return UnexpectedGame(d, g, fp, lp)


class GameUiBuilder:

    def __init__(self, d: BaseDisplay, g: Game):
        self.d = d
        self.g = g
        self.b = View.create_image(d.size)
        self.ry = View.create_image(d.size)

    def deploy(self):
        self.d.update(self.b, self.ry)


class NoGame(GameUiBuilder):

    def __init__(self, d: BaseDisplay, fp: FontProvider):
        # noinspection PyTypeChecker
        super().__init__(d, g=None)

        message = 'No upcoming games'

        SpacingLayout(0.05,
                      TextView(message, fp)) \
            .draw(self.b, self.ry)


class LiveGame(GameUiBuilder):

    def __init__(self, d: BaseDisplay, g: Game, fp: FontProvider, lp: LogoProvider):
        super().__init__(d, g)
        self.fp = fp
        self.lp = lp

        en = 'EN'

        side_column_weights = [2, 1]

        away_column = LinearLayout([
            TeamLogo(self.g.away, self.lp, p=View.start_start),
            TextView(en, self.fp, invert_colors=True) if self.g.details.away.goalie_pulled else Empty()
        ], side_column_weights, is_vertical=True)

        score_font_size = 40
        period_info = f'{self.g.details.period_ordinal}\n{self.g.details.period_remaining}'
        center_top = LinearLayout([
            TextView(f'{self.g.away.score}', self.fp, max_size=score_font_size, p=View.end_center),
            TextView(period_info, self.fp),
            TextView(f'{self.g.home.score}', self.fp, max_size=score_font_size, p=View.start_center)
        ], [1, 2, 1])

        center_bottom = Empty()

        if self.g.details.in_pp:

            if self.g.details.away.in_pp or self.g.details.home.in_pp:
                pp = 'PP'
                pp_remaining = None
                if self.g.details.in_pp:
                    pp_remaining = utils.pp_seconds_to_friendly(self.g.details.pp_remaining_seconds)

                center_bottom = LinearLayout([
                    TextView(pp, self.fp, invert_colors=True) if self.g.details.away.in_pp else Empty(),
                    TextView(pp_remaining, self.fp) if self.g.details.in_pp else Empty(),
                    TextView(pp, self.fp, invert_colors=True) if self.g.details.home.in_pp else Empty(),
                ], [1, 2, 1])
            else:
                event = f'{self.g.details.away.num_skaters}-on-{self.g.details.home.num_skaters}'
                event_remaining = None
                if self.g.details.in_pp:
                    event_remaining = utils.pp_seconds_to_friendly(self.g.details.pp_remaining_seconds)

                center_bottom = LinearLayout([
                    TextView(en, self.fp, invert_colors=True) if self.g.details.away.goalie_pulled else Empty(),
                    TextView(f'{event}\n{event_remaining}', self.fp),
                    TextView(en, self.fp, invert_colors=True) if self.g.details.home.goalie_pulled else Empty(),
                ], [1, 4, 1])

        center_column = LinearLayout([
            center_top,
            center_bottom
        ], [2, 1], is_vertical=True)

        home_column = LinearLayout([
            TeamLogo(self.g.home, self.lp, p=View.end_start),
            TextView(en, self.fp, invert_colors=True) if self.g.details.home.goalie_pulled else Empty()
        ], side_column_weights, is_vertical=True)

        all_columns = LinearLayout([away_column, center_column, home_column], [2, 5, 2])
        SpacingLayout(0.02, all_columns).draw(self.b, self.ry)


class ScheduledGame(GameUiBuilder):

    def __init__(self, d: BaseDisplay, g: Game, fp: FontProvider, lp: LogoProvider):
        super().__init__(d, g)
        self.fp = fp
        self.lp = lp

        icon_record_weights = [4, 1]

        away_column = LinearLayout([
            TeamLogo(self.g.away, self.lp, p=View.center_start),
            TeamRecord(self.g.away, self.fp, p=View.center_end)
        ], icon_record_weights, is_vertical=True)

        text = self.get_time(g)
        date_time_column = TextView(text, self.fp)

        home_column = LinearLayout([
            TeamLogo(self.g.home, self.lp, p=View.center_start),
            TeamRecord(self.g.home, self.fp, p=View.center_end)
        ], icon_record_weights, is_vertical=True)

        LinearLayout([away_column, date_time_column, home_column], [3, 4, 3]) \
            .draw(self.b, self.ry)

    def get_time(self, g):
        day, time, tz = get_friendly_game_time(g, to_tz=pytz.timezone(config.TIMEZONE))
        return f'\n@\n\n{day}\n{time}\n({tz})'


class ScheduledTimeTbdGame(ScheduledGame):

    def __init__(self, d: BaseDisplay, g: Game, fp: FontProvider, lp: LogoProvider):
        super().__init__(d, g, fp, lp)

    def get_time(self, g):
        # Time is TBD, force-add 3 hours to show correct day of game in most continental US timezones
        g.datetime_utc += timedelta(hours=3)
        day, time, tz = get_friendly_game_time(g, to_tz=pytz.timezone(config.TIMEZONE))
        return f'\n@\n\n{day}\nTime TBD'


class PostponedGame(ScheduledGame):

    def __init__(self, d: BaseDisplay, g: Game, fp: FontProvider, lp: LogoProvider):
        super().__init__(d, g, fp, lp)

    def get_time(self, g):
        # Postponed but just like in ScheduledTimeTbdGame...
        # Force-add 3 hours to show correct day of game in most continental US timezones
        g.datetime_utc += timedelta(hours=3)
        day, time, tz = get_friendly_game_time(g, to_tz=pytz.timezone(config.TIMEZONE))
        return f'\n@\n\n{day}\nPostponed'


class FinalGame(GameUiBuilder):

    def __init__(self, d: BaseDisplay, g: Game, fp: FontProvider, lp: LogoProvider):
        super().__init__(d, g)
        self.fp = fp
        self.lp = lp

        logo_spacing = 0.05
        away_column = LinearLayout([
            SpacingLayout(logo_spacing, TeamLogo(self.g.away, self.lp)),
            TeamRecord(self.g.away, self.fp, p=View.center_end)
        ], [3, 1], is_vertical=True)

        score_max_size = 45
        scores = LinearLayout([
            TextView(str(self.g.away.score), self.fp, max_size=score_max_size),
            TextView('@', self.fp, max_size=22),
            TextView(str(self.g.home.score), self.fp, max_size=score_max_size)
        ], [2, 2, 2])

        status_str = 'Final'
        if g.details is not None and g.details.period > 3:
            status_str += f'/{g.details.period_ordinal}'

        status = TextView(status_str, fp, p=View.center_start)
        score_column = LinearLayout([scores, status], [3, 2], is_vertical=True)

        home_column = LinearLayout([
            SpacingLayout(logo_spacing, TeamLogo(self.g.home, self.lp)),
            TeamRecord(self.g.home, self.fp, p=View.center_end)
        ], [3, 1], is_vertical=True)

        SpacingLayout(0.05, LinearLayout([away_column, score_column, home_column], [3, 4, 3])) \
            .draw(self.b, self.ry)


class UnexpectedGame(GameUiBuilder):
    def __init__(self, d: BaseDisplay, g: Game, fp: FontProvider, lp: LogoProvider):
        super().__init__(d, g)

        day, time, tz = get_friendly_game_time(g, to_tz=pytz.timezone(config.TIMEZONE))
        date_time = TextView(f'\n@\n\n{day}\n{time}\n({tz})', fp)

        message = f'Unexpected game (status={self.g.original_status})'

        SpacingLayout(0.05,
                      LinearLayout([
                          LinearLayout([
                              TeamLogo(self.g.away, lp),
                              date_time,
                              TeamLogo(self.g.home, lp),
                          ]),
                          TextView(message, fp, max_size=15, p=View.center_end)
                      ], [6, 1], is_vertical=True))\
            .draw(self.b, self.ry)


# Custom Views


class Empty(View):

    def draw(self, im: Image, im_ry: Image = None):
        pass


class TeamRecord(View):
    def __init__(self, t: Team, fp: FontProvider, p=View.center_center):

        record = f'{t.wins}-{t.losses}'

        if t.ot is not None:
            record = record + f'-{t.ot}'

        self.r = f'({record})'
        self.fp = fp
        self.p = p

    def draw(self, im_b: Image, im_ry: Image = None):
        TextView(self.r, self.fp, max_size=16, p=self.p).draw(im_b, im_ry)


class TeamLogo(View):
    def __init__(self, t: Team, lp: LogoProvider, p=View.center_center):
        self.b_path, self.ry_path = lp.get_team_logo_path(t.id)
        self.p = p

    def draw(self, im: Image, im_ry: Image = None):

        try:
            ImagePathView(self.b_path, self.ry_path, p=self.p).draw(im, im_ry)
        except FileNotFoundError:
            SpacingLayout(0.15,
                          MissingDataView()) \
                .draw(im, im_ry)
