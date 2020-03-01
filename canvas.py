from display import *
from game import Game, GameStatus
from PIL import Image, ImageDraw, ImageFont
import os
from utils import get_friendly_local_date, LogoProvider, FontProvider
import constants


class Canvas(object):

    def __init__(self, display: BaseDisplay, font_provider: FontProvider):
        self.display = display
        self.font_provider = font_provider
        self.size_to_font = dict()
        self.b = self.__new_image(self.display)
        self.canvas_b = self.__new_canvas(self.b)
        self.ry = self.__new_image(self.display)
        self.canvas_ry = self.__new_canvas(self.ry)

    @staticmethod
    def __new_image(display: BaseDisplay):
        return Image.new('1', (display.size[0], display.size[1]), 255)

    @staticmethod
    def __new_canvas(im: Image):
        return ImageDraw.Draw(im)

    def get_font_by_size(self, size: int):
        key = str(size)
        if self.size_to_font.get(key) is None:
            font = self.font_provider.get_font_path_filename()
            self.size_to_font[key] = ImageFont.truetype(font, size)
        return self.size_to_font[key]

    @staticmethod
    def get_center_left(canvas_wh: tuple, obj_size_wh: tuple, margin):
        return int(margin), int((canvas_wh[1] - obj_size_wh[1]) / 2)

    @staticmethod
    def get_center_right(canvas_wh: tuple, obj_size_wh: tuple, margin):
        return int(canvas_wh[0] - obj_size_wh[0] - margin), int((canvas_wh[1] - obj_size_wh[1]) / 2)

    @staticmethod
    def get_center(canvas_wh: tuple, obj_size_wh: tuple, offset_xy: tuple = (0, 0)):
        x = ((canvas_wh[0] - obj_size_wh[0]) / 2) + offset_xy[0]
        y = ((canvas_wh[1] - obj_size_wh[1]) / 2) + offset_xy[1]
        return int(x), int(y)

    @staticmethod
    def get_prepared_canvas(display: BaseDisplay, font_provider: FontProvider,
                            game: Game, icon_provider: LogoProvider, days_delta: int):

        if GameStatus.SCHEDULED == game.status:
            return ScheduledGameCanvas(display, font_provider, game, icon_provider, days_delta)
        elif GameStatus.FINAL == game.status:
            return FinalGameCanvas(display, font_provider, game, icon_provider)
        else:
            return UnexpectedGameCanvas(display, font_provider, game)

    def draw(self):
        self.display.update(self.b, self.ry)


class ScheduledGameCanvas(Canvas):

    def __init__(self, d: BaseDisplay, fp: FontProvider, g: Game, lp: LogoProvider, days_delta: int):
        super().__init__(d, fp)

        draw_logos(self, g, lp, constants.CANVAS_LOGOS_EDGE_SPACING)

        day, time, tz = get_friendly_local_date(g, days_delta)
        text = f'@\n_____\n{day}\n{time}\n({tz})'
        text_font = super().get_font_by_size(18)
        text_xy = super().get_center(self.display.size, self.canvas_b.textsize(text, text_font))
        self.canvas_b.multiline_text(text_xy, text, font=text_font, align='center')


class FinalGameCanvas(Canvas):

    def __init__(self, d: BaseDisplay, fp: FontProvider, g: Game, lp: LogoProvider):
        super().__init__(d, fp)

        draw_logos(self, g, lp, constants.CANVAS_LOGOS_EDGE_SPACING, (0, -4))
        draw_records(self, g)

        at = "@"
        at_font = super().get_font_by_size(20)
        at_xy = super().get_center(self.display.size, self.canvas_b.textsize(at, font=at_font))
        self.canvas_b.text(at_xy, at, font=at_font)

        score_font = super().get_font_by_size(60)
        score_offset = int(0.04 * d.size[0])
        display_center = super().get_center(d.size, (0, 0))

        away_score_size = self.canvas_b.textsize(str(g.away.score), score_font)
        away_score_xy = (display_center[0] - away_score_size[0] - score_offset,
                         display_center[1] - (away_score_size[1]/2))
        self.canvas_b.text(away_score_xy, str(g.away.score), font=score_font)

        home_score_size = self.canvas_b.textsize(str(g.home.score), score_font)
        home_score_xy = (display_center[0] + score_offset,
                         display_center[1] - home_score_size[1]/2)
        self.canvas_b.text(home_score_xy, str(g.home.score), font=score_font)

        final = 'Final'
        final_font = super().get_font_by_size(22)
        final_size = self.canvas_b.textsize(final, font=final_font)
        final_xy = (display_center[0] - (final_size[0]/2), d.size[1] - final_size[1])
        self.canvas_b.text(final_xy, final, font=final_font)


class UnexpectedGameCanvas(Canvas):

    def __init__(self, display: BaseDisplay, font_provider: FontProvider, game: Game):
        super().__init__(display, font_provider)

        error_font_size = 16
        error_font = super().get_font_by_size(error_font_size)
        error_str = f'Unexpected game (status={game.status})'
        error_xy = (0, display.size[1] - error_font_size)
        self.canvas_b.text(error_xy, error_str, font=error_font)


def draw_logos(c: Canvas, g: Game, lp: LogoProvider, edge_spacing=0, offset=(0, 0)):

    # Moving forward *_b images are assumed to exist, *_ry are checked via os.path.exists()

    factor = 0.65
    c.display.size = (296, 128)
    new_size = (int(factor * c.display.size[0]), int(factor * c.display.size[1]))
    home_b_path, home_ry_path = lp.get_team_logo_path(g.home.id)
    home_b = Image.open(home_b_path)
    home_b.thumbnail(new_size)
    home_xy = c.get_center_right(c.display.size, home_b.size, edge_spacing)
    home_xy = (home_xy[0] + offset[0], home_xy[1] + offset[1])
    c.b.paste(home_b, home_xy)
    if os.path.exists(home_ry_path):
        home_ry = Image.open(home_ry_path)
        home_ry.thumbnail(new_size)
        c.ry.paste(home_ry, home_xy)

    away_b_path, away_ry_path = lp.get_team_logo_path(g.away.id)
    away_b = Image.open(away_b_path)
    away_b.thumbnail(new_size)
    away_xy = c.get_center_left(c.display.size, away_b.size, edge_spacing)
    away_xy = (away_xy[0] + offset[0], away_xy[1] + offset[1])
    c.b.paste(away_b, away_xy)
    if os.path.exists(away_ry_path):
        away_ry = Image.open(away_ry_path)
        away_ry.thumbnail(new_size)
        c.ry.paste(away_ry, away_xy)


def draw_records(c: Canvas, g: Game):

    record_font = c.get_font_by_size(15)

    away_record = f'({g.away.wins}-{g.away.losses}-{g.away.ot})'
    away_record_size = c.canvas_b.textsize(away_record, record_font)
    away_record_xy = (0, c.display.size[1] - away_record_size[1])
    c.canvas_b.text(away_record_xy, away_record, font=record_font)

    home_record = f'({g.home.wins}-{g.home.losses}-{g.home.ot})'
    home_record_size = c.canvas_b.textsize(home_record, record_font)
    home_record_xy = (c.display.size[0] - home_record_size[0], c.display.size[1] - home_record_size[1])
    c.canvas_b.text(home_record_xy, home_record, font=record_font)
