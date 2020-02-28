import os
import sys

libraries = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libs')
if os.path.exists(libraries):
    sys.path.append(libraries)

# noinspection PyUnresolvedReferences
from waveshare_epd import epd2in9bc
import logging
from time import sleep


class Display:
    def __init__(self):
        self.epd = epd2in9bc.EPD()
        self.size = (self.epd.height, self.epd.width)  # Display always used horizontal (H x W)
        self.log = logging
        self.log.basicConfig(level=logging.DEBUG)
        self.is_initialized = False

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

    def update(self, b, ry):
        if self.epd and b and ry:
            self.epd.display(self.epd.getbuffer(b), self.epd.getbuffer(ry))
        else:
            self.log.error(f'Missing requirements for the display: ({self.epd}, {b}, {ry})')
