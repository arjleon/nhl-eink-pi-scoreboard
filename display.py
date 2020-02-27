import os
import sys

libraries = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libs')
if os.path.exists(libraries):
    sys.path.append(libraries)
images = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'imgs')

# noinspection PyUnresolvedReferences
from waveshare_epd import epd2in9bc
import logging
from time import sleep
from PIL import Image, ImageDraw, ImageFont


class Display:
    def __init__(self):
        self.epd = epd2in9bc.EPD()
        self.log = logging
        self.log.basicConfig(level=logging.DEBUG)
        self.is_initialized = False
        self.font_big = ImageFont.truetype(os.path.join(images, 'Font.ttc'), 24)

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

    def show_finished_game(self, score_away, score_home):
        b = self.__new_image()
        canvas_b = self.__new_canvas(b)
        self.__center_text(canvas_b, f'{score_away} - {score_home}', font=self.font_big)
        self.__center_text(canvas_b, 'Final', offset=(0, 30), font=self.font_big)

        ry = self.__new_image()

        self.__update(b, ry)

    def __new_image(self):
        return Image.new('1', (self.epd.height, self.epd.width), 255)

    @staticmethod
    def __new_canvas(image):
        return ImageDraw.Draw(image)

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
