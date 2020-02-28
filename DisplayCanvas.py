from display import Display
from game import Game
from PIL import Image, ImageDraw, ImageFont
import os
from utils import get_friendly_local_date, TeamIconProvider, FontProvider


class BaseDisplayCanvas(object):

    def __init__(self, display: Display, font_provider: FontProvider):
        self.display = display
        self.font_provider = font_provider
        self.size_to_font = []
        self.b = self.__new_image()
        self.ry = self.__new_image()

    def __new_image(self):
        # New image will take in height (index 1) and width (index 0) for horizontal orientation:
        return Image.new('1', (self.display.size[1], self.display.size[0]), 255)

    def get_font_by_size(self, size: int):
        key = str(size)
        if self.size_to_font[key] is None:
            filename = os.path.join(self.font_provider.get_font_path(), 'Font.ttc')
            self.size_to_font[key] = ImageFont.truetype(filename, size)
        return self.size_to_font[key]

    @staticmethod
    def get_center_left(canvas_wh: tuple, obj_size_wh: tuple, margin):
        return int(margin), int((canvas_wh[1] - obj_size_wh[1])/2)

    @staticmethod
    def get_center_right(canvas_wh: tuple, obj_size_wh: tuple, margin):
        return int(canvas_wh[0] - obj_size_wh[0] - margin), int((canvas_wh[1] - obj_size_wh[1])/2)

    @staticmethod
    def get_center(canvas_wh: tuple, obj_size_wh: tuple, offset_xy: tuple = (0, 0)):
        x = ((canvas_wh[0]-obj_size_wh[0])/2) + offset_xy[0]
        y = ((canvas_wh[1]-obj_size_wh[1])/2) + offset_xy[1]
        return int(x), int(y)

    def draw(self):
        self.display.update(self.b, self.ry)


class UpcomingGameCanvas(BaseDisplayCanvas):

    def __init__(self, display: Display, font_provider: FontProvider,
                 game: Game, icon_provider: TeamIconProvider, days_delta: int):
        super().__init__(display, font_provider)

        # Moving forward *_b images are assumed to exist, *_ry are checked via os.path.exists()

        icon_margin = int(0.03 * min(self.display.size))

        home_icon_b_path, home_icon_ry_path = icon_provider.get_team_icon_path(game.home.id)
        home_icon_b = Image.open(home_icon_b_path)
        home_icon_xy = super().get_center_right(self.display.size, home_icon_b.size, icon_margin)
        self.b.paste(home_icon_b, home_icon_xy)
        if os.path.exists(home_icon_ry_path):
            home_icon_ry = Image.open(home_icon_ry_path)
            self.ry.paste(home_icon_ry, home_icon_xy)

        away_icon_b_path, away_icon_ry_path = icon_provider.get_team_icon_path(game.away.id)
        away_icon_b = Image.open(away_icon_b_path)
        away_icon_xy = super().get_center_left(self.display.size, away_icon_b.size, icon_margin)
        self.b.paste(away_icon_b, away_icon_xy)
        if os.path.exists(away_icon_ry_path):
            away_icon_ry = Image.open(away_icon_ry_path)
            self.ry.paste(away_icon_ry, away_icon_xy)

        friendly_date = get_friendly_local_date(game, days_delta)

        date_font = super().get_font_by_size(15)
        canvas_b = ImageDraw.Draw(self.b)
        date_xy = super().get_center(self.display.size, canvas_b.textsize(friendly_date, date_font))
        canvas_b.text(date_xy, friendly_date, font=date_font)
