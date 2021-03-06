import os
import sys
import logging
from time import sleep

libraries = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libs')
if os.path.exists(libraries):
    sys.path.append(libraries)

try:
    # noinspection PyUnresolvedReferences
    from waveshare_epd import epd2in9bc
except OSError:
    pass


def get_display():
    try:
        return Epd2in9bcDisplay()
    except NameError:
        return FakeEpd2in9bcDisplay()


class BaseDisplay:

    def __init__(self, width: int = 0, height: int = 0):
        self.size = (width, height)

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()

    def update(self, b, ry):
        raise NotImplementedError()


class FakeEpd2in9bcDisplay(BaseDisplay):

    def __init__(self):
        super().__init__(296, 128)
        print(f'{self.__class__.__name__} init')
        debug_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'res', 'debug')
        self.debug_path_b = os.path.join(debug_path, 'display-b.gif')
        self.debug_path_ry = os.path.join(debug_path, 'display-ry.gif')

    def start(self):
        pass

    def stop(self):
        pass

    def clear(self):

        try:
            os.remove(self.debug_path_b)
            os.remove(self.debug_path_ry)
        except:
            pass

    def update(self, b, ry):

        b.save(self.debug_path_b)
        ry.save(self.debug_path_ry)


class Epd2in9bcDisplay(BaseDisplay):

    def __init__(self):
        self.epd = epd2in9bc.EPD()
        super().__init__(self.epd.height, self.epd.width)  # Display always used horizontal (H x W)
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
            self.log.info(f'Updating {self.__class__.__name__}')
            self.epd.display(self.epd.getbuffer(b), self.epd.getbuffer(ry))
        else:
            self.log.error(f'Missing requirements for the display: ({self.epd}, {b}, {ry})')
