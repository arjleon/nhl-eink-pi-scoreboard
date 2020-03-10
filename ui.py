from display import *
from layout import *
from utils import *
from game import *


def get_ui_builder(d: BaseDisplay, fp: FontProvider, lp: LogoProvider, g: Game):
    if GameStatus.FINAL == g.status:
        return FinalGame(d, g, fp, lp)


class GameUiBuilder:

    def __init__(self, d: BaseDisplay, g: Game):
        self.d = d
        self.g = g
        self.b = View.create_image(d.size)
        self.ry = View.create_image(d.size)

    def deploy(self):
        self.d.update(self.b, self.ry)


class FinalGame(GameUiBuilder):

    def __init__(self, d: BaseDisplay, g: Game, fp: FontProvider, lp: LogoProvider):
        super().__init__(d, g)
        self.fp = fp
        self.lp = lp

        logo_spacing = 0.05
        away_b_path, away_ry_path = self.lp.get_team_logo_path(self.g.away.id)
        away_record = f'{self.g.away.wins}-{self.g.away.losses}-{self.g.away.ot}'
        away_column = LinearLayout([
            SpacingLayout(logo_spacing, ImagePathView(away_b_path, away_ry_path)),
            TextView(away_record, self.fp, p=View.center_end)
        ], [3, 1], is_vertical=True)

        score_max_size = 45
        scores = LinearLayout([
            TextView(str(self.g.away.score), self.fp, max_size=score_max_size),
            TextView('@', self.fp, max_size=25),
            TextView(str(self.g.home.score), self.fp, max_size=score_max_size)
        ], [2, 2, 2])
        status = TextView('Final', fp, p=View.center_start)
        score_column = LinearLayout([scores, status], [3, 2], is_vertical=True)

        home_b_path, home_ry_path = self.lp.get_team_logo_path(self.g.home.id)
        home_record = f'{self.g.home.wins}-{self.g.home.losses}-{self.g.home.ot}'
        home_column = LinearLayout([
            SpacingLayout(logo_spacing, ImagePathView(home_b_path, home_ry_path)),
            TextView(home_record, self.fp, p=View.center_end)
        ], [3, 1], is_vertical=True)

        SpacingLayout(0.05, LinearLayout([away_column, score_column, home_column], [3, 4, 3])) \
            .draw(self.b, self.ry)


class RecordsRow(View):
    def __init__(self, away: str, home: str, fp: FontProvider):
        self.a = away
        self.h = home
        self.fp = fp

    def draw(self, im_b: Image, im_ry: Image = None):
        LinearLayout([
            TextView(self.a, self.fp, p=View.start_center),
            TextView(self.h, self.fp, p=View.end_center)
        ]).draw(im_b, im_ry)
