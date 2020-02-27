import os
import sys

libraries = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libs')
if os.path.exists(libraries):
    sys.path.append(libraries)
res = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'res')

# noinspection PyUnresolvedReferences
from waveshare_epd import epd2in9bc
import logging
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from game import Game


class Display:
    def __init__(self):
        self.epd = epd2in9bc.EPD()
        self.size = (self.epd.height, self.epd.width)  # Display always used horizontal (H x W)
        self.log = logging
        self.log.basicConfig(level=logging.DEBUG)
        self.is_initialized = False
        self.font_big = ImageFont.truetype(os.path.join(res, 'Font.ttc'), 24)

    def start(self):
        if self.is_initialized:
            self.log.error('Cannot start; already initialized')
            return
        if self.epd:
            self.log.info('Starting')
            self.is_initialized = True
            self.epd.init()
            sleep(1)

    def stop(self):
        if not self.is_initialized:
            self.log.error('Cannot stop; not initialized')
            return
        if self.epd:
            self.log.info('Stopping')
            self.epd.sleep()
            self.is_initialized = False
            sleep(1)

    def clear(self):
        if self.epd:
            self.log.info('Clearing')
            self.epd.Clear()
            sleep(1)

# TODO: Should abbreviations be part of Game's Team objects? Display stages filling gaps before drawing?
    def show_finished_game(self, g: Game, away_abbr, home_abbr):

        b = self.__new_image()
        ry = self.__new_image()

        (away_b, away_ry) = self.__get_team_icons(away_abbr)
        (home_b, home_ry) = self.__get_team_icons(home_abbr)

        # Margin proportional to display size
        base_margin = 0.03 * self.size[0]
        # Away/left icon: left based on margin, and center vertically based on b image
        away_xy = (base_margin, (self.size[1] - away_b.size[1])/2)
        # Home/right icon: left based on display size - image width - margin, and center vertically based on b image
        home_xy = (self.size[0] - home_b.size[0] - base_margin, (self.size[1] - home_b.size[1])/2)

        b.paste(away_b, away_xy)
        b.paste(home_b, home_xy)
        # Code will assume b and ry images are the same size; reusing measured positions
        if away_ry:
            ry.paste(away_ry, away_xy)
        if home_ry:
            ry.paste(home_ry, home_xy)

        canvas_b = self.__new_canvas(b)
        self.__center_text(canvas_b, f'{g.away.score} - {g.home.score}', font=self.font_big)
        self.__center_text(canvas_b, 'Final', offset=(0, 30), font=self.font_big)

        self.__update(b, ry)

    def __new_image(self):
        return Image.new('1', (self.epd.height, self.epd.width), 255)

    @staticmethod
    def __new_canvas(image):
        return ImageDraw.Draw(image)

    @staticmethod
    def __get_team_icons(abbr):
        ext = '.gif'

        b_path = os.path.join(res, f'{abbr}-b{ext}')
        b = None
        if os.path.exists(b_path):
            b = Image.open(b_path)

        ry_path = os.path.join(res, f'{abbr}-ry{ext}')
        ry = None
        if os.path.exists(ry_path):
            ry = Image.open(ry_path)

        return b, ry

    @staticmethod
    def __center_text(canvas: ImageDraw, text, offset: tuple = (0, 0), font=None, fill=0):
        (cw, ch) = canvas.im.size
        (tw, th) = canvas.textsize(text=text, font=font)
        (x, y) = (((cw-tw)/2) + offset[0], ((ch-th)/2) + offset[1])
        canvas.text((x, y), text, font=font, fill=0)

    def __update(self, b, ry):
        if self.epd and b and ry:
            self.epd.display(self.epd.getbuffer(b), self.epd.getbuffer(ry))
        else:
            self.log.error(f'Missing requirements for the display: ({self.epd}, {b}, {ry})')
