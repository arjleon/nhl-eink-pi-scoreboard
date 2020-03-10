from PIL import Image, ImageDraw, ImageFont
from enum import Enum, auto
from utils import FontProvider
import os


class View:

    def draw(self, im: Image, im_ry: Image = None):
        raise NotImplementedError()

    @staticmethod
    def create_image(size):
        return Image.new('1', size, 255)

    @staticmethod
    def create_canvas(im: Image):
        canvas = ImageDraw.Draw(im)
        return canvas

    @staticmethod
    def xy(box, el, pos):

        x, y = (0, 0)  # Assumed default of View.Pos.start for both x and y

        delta_x = box[0] - el[0]
        delta_y = box[1] - el[1]

        if pos[0] is View.__Pos.end:
            x = delta_x
        elif pos[0] is View.__Pos.center:
            x = delta_x / 2

        if pos[1] is View.__Pos.end:
            y = delta_y
        elif pos[1] is View.__Pos.center:
            y = delta_y / 2

        return int(x), int(y)

    class __Pos(Enum):
        start = auto()
        center = auto()
        end = auto()

    start_start = (__Pos.start, __Pos.start)
    start_center = (__Pos.start, __Pos.center)
    start_end = (__Pos.start, __Pos.end)
    center_start = (__Pos.center, __Pos.start)
    center_center = (__Pos.center, __Pos.center)
    center_end = (__Pos.center, __Pos.end)
    end_start = (__Pos.end, __Pos.start)
    end_center = (__Pos.end, __Pos.center)
    end_end = (__Pos.end, __Pos.end)


class TextView(View):

    def __init__(self, text: str, font_provider: FontProvider, max_size=20, invert_colors=False,
                 p=View.center_center):

        self.t = text
        self.fp = font_provider
        self.ms = max_size
        self.p = p
        self.inv = invert_colors

    def get_font(self, s):
        return ImageFont.truetype(self.fp.get_font_path_filename(), s)

    def draw(self, im: Image, im_ry: Image = None):

        canvas = View.create_canvas(im)
        font_size = self.ms
        font = self.get_font(font_size)
        text_size = canvas.textsize(self.t, font)
        while text_size[0] > 8 and text_size[1] > 8 \
                and (text_size[0] > im.size[0] or text_size[1] > im.size[1]):
            font_size -= 2
            font = self.get_font(font_size)
            text_size = canvas.textsize(self.t, font)

        xy = View.xy(im.size, text_size, self.p)

        bg_fill = 0 if self.inv else 255
        canvas.rectangle((xy, (xy[0] + text_size[0], xy[1] + text_size[1])), fill=bg_fill)

        text_fill = 255 if self.inv else 0
        canvas.multiline_text(xy, self.t, fill=text_fill, font=font, align='center')


class ImagePathView(View):

    def __init__(self, im_path: str, im_ry_path: str, p=View.center_center):
        self.im_path = im_path
        self.im_ry_path = im_ry_path
        self.p = p

    def draw(self, im: Image, im_ry: Image = None):
        _im_b = Image.open(self.im_path)
        new_max_size = (int(min(im.size[0], _im_b.size[0])), int(min(im.size[1], _im_b.size[1])))
        _im_b.thumbnail(new_max_size)
        new_size = _im_b.size
        xy = View.xy(im.size, new_size, self.p)
        im.paste(_im_b, xy)
        _im_b.close()

        if im_ry is not None and os.path.exists(self.im_ry_path):
            _im_ry = Image.open(self.im_ry_path)
            _im_ry.thumbnail(new_size)
            im_ry.paste(_im_ry, xy)
            _im_ry.close()


class SpacingLayout(View):

    def __init__(self, spacing_percent, child):
        self.s = spacing_percent
        self.c = child

    def draw(self, im: Image, im_ry: Image = None):
        x_space = int(im.size[0] * self.s)
        y_space = int(im.size[1] * self.s)
        xy = (x_space, y_space)
        new_size = (int(im.size[0] - (x_space * 2)), int(im.size[1] - (y_space * 2)))
        new_image = View.create_image(new_size)
        new_image_ry = View.create_image(new_size)
        self.c.draw(new_image, new_image_ry)
        im.paste(new_image, xy)
        if im_ry is not None:
            im_ry.paste(new_image_ry, xy)


class LinearLayout(View):

    def __init__(self, children: [], weights: [int] = None, is_vertical=False):

        if children is None or len(children) == 0:
            raise ValueError('Missing children', children)

        if weights is None:
            weights = [1] * len(children)

        if len(children) != len(weights):
            raise ValueError('Mismatch', len(children), len(weights))

        self.children = children
        self.weights = weights
        self.weights_total = 0
        self.is_vertical = is_vertical

        for w in weights:
            self.weights_total += w

    def draw(self, im: Image, im_ry: Image = None):

        x, y = (0, 0)
        w, h = im.size
        for i in range(len(self.children)):
            c = self.children[i]
            percent = self.weights[i] / self.weights_total

            new_w = 0
            new_h = 0
            if self.is_vertical:
                new_h = int(percent * h)
                new_size = (w, new_h)
            else:
                new_w = int(percent * w)
                new_size = (new_w, h)

            new_image = View.create_image(new_size)
            new_image_ry = View.create_image(new_size)
            c.draw(new_image, new_image_ry)
            im.paste(new_image, (x, y))
            if im_ry is not None:
                im_ry.paste(new_image_ry, (x, y))
            x += new_w
            y += new_h
            del c, percent, new_w, new_h, new_size, new_image, new_image_ry
