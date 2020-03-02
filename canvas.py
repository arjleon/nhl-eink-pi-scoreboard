from display import *
from game import Game, GameStatus, GameDetails, GameDetailsTeam
from PIL import Image, ImageDraw, ImageFont
import os
from utils import *
import constants
import pytz


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
                            game: Game, logo_provider: LogoProvider):

        if GameStatus.SCHEDULED == game.status:
            return ScheduledGameCanvas(display, font_provider, game, logo_provider)
        elif (GameStatus.LIVE == game.status or GameStatus.LIVE_CRITICAL == game.status) and game.has_details():
            return LiveGame(display, font_provider, game, logo_provider)
        elif GameStatus.FINAL == game.status:
            return FinalGameCanvas(display, font_provider, game, logo_provider)
        else:
            return UnexpectedGameCanvas(display, font_provider, game)

    def draw(self):
        self.display.update(self.b, self.ry)


class ScheduledGameCanvas(Canvas):

    def __init__(self, d: BaseDisplay, fp: FontProvider, g: Game, lp: LogoProvider):
        super().__init__(d, fp)

        draw_logos(self, g, lp, constants.CANVAS_LOGOS_EDGE_SPACING, scale=0.65)
        draw_records(self, g)

        day, time, tz = get_friendly_game_time(g, to_tz=pytz.timezone('US/Pacific'))
        text = f'@\n_____\n{day}\n{time}\n({tz})'
        text_font = super().get_font_by_size(18)
        text_xy = super().get_center(self.display.size, self.canvas_b.textsize(text, text_font))
        self.canvas_b.multiline_text(text_xy, text, font=text_font, align='center')


class LiveGame(Canvas):

    def __init__(self, d: BaseDisplay, fp: FontProvider, g: Game, lp: LogoProvider):
        super().__init__(d, fp)

        logos_offset = (0, -int((0.2 * d.size[1])))
        draw_logos(self, g, lp, constants.CANVAS_LOGOS_EDGE_SPACING, logos_offset, scale=0.5)

        score_font = super().get_font_by_size(60)
        score_offset = (int(0.1 * d.size[0]), int(0.1 * d.size[0]))
        display_center = super().get_center(d.size, (0, 0))

        away_score_size = self.canvas_b.textsize(str(g.away.score), score_font)
        away_score_xy = (display_center[0] - away_score_size[0] - score_offset[0],
                         display_center[1] - (away_score_size[1] / 2) - score_offset[1])
        self.canvas_b.text(away_score_xy, str(g.away.score), font=score_font)

        home_score_size = self.canvas_b.textsize(str(g.home.score), score_font)
        home_score_xy = (display_center[0] + score_offset[0],
                         display_center[1] - (home_score_size[1] / 2) - score_offset[1])
        self.canvas_b.text(home_score_xy, str(g.home.score), font=score_font)

        period_font = super().get_font_by_size(20)
        period = f'{g.details.period}\n{g.details.period_remaining}'
        period_size = self.canvas_b.textsize(period, period_font)
        period_xy = (int(display_center[0] - period_size[0]/2),
                     int(display_center[1] - period_size[1]/2 - score_offset[1]))
        self.canvas_b.multiline_text(period_xy, period, font=period_font, align='center')

        if g.details.in_pp:
            pp = 'PP'
            pp_offset = score_offset

            if g.details.away.in_pp:
                pp_offset = (pp_offset[0] * -1, pp_offset[1])

            pp_font = self.get_font_by_size(20)
            pp_size = self.canvas_b.textsize(pp, pp_font)
            pp_size_max = int(max(pp_size[0], pp_size[1]))
            pp_outline_size = (pp_size_max, pp_size_max)
            pp_im = Image.new('1', pp_outline_size, 255)
            pp_can = ImageDraw.Draw(pp_im)
            pp_can.rectangle(((0, 0), pp_outline_size), fill=0)
            pp_can.text((0, 0), pp, font=pp_font, fill=255)
            pp_xy = (int(display_center[0] - pp_im.size[0]/2 + pp_offset[0] * 1.5),
                     int(display_center[1] - pp_im.size[1]/2 + pp_offset[1]))

            pp_time_font = self.get_font_by_size(15)
            pp_time = pp_seconds_to_friendly(g.details.pp_remaining_seconds)
            pp_time_size = self.canvas_b.textsize(pp_time, font=pp_time_font)
            pp_time_xy = (int(display_center[0] - pp_time_size[0]/2),
                          int(display_center[1] - pp_time_size[1]/2 + pp_offset[1]))
            self.canvas_b.text(pp_time_xy, pp_time, font=pp_time_font)

            self.b.paste(pp_im, pp_xy)


class FinalGameCanvas(Canvas):

    def __init__(self, d: BaseDisplay, fp: FontProvider, g: Game, lp: LogoProvider):
        super().__init__(d, fp)

        draw_logos(self, g, lp, constants.CANVAS_LOGOS_EDGE_SPACING, (0, -4), scale=0.65)
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


def draw_logos(c: Canvas, g: Game, lp: LogoProvider, edge_spacing=0, offset=(0, 0), scale=1.0):

    # Moving forward *_b images are assumed to exist, *_ry are checked via os.path.exists()

    new_size = (int(scale * c.display.size[0]), int(scale * c.display.size[1]))

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
